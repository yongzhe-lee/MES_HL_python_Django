import io, os, mimetypes, uuid, zipfile
from pathlib import Path

from io import BytesIO
from lxml import etree

from typing import List, Optional, Tuple, Any


from configurations import settings
from django.http import FileResponse


from basyx.aas.model import DictObjectStore, MultiLanguageNameType, MultiLanguageTextType, Submodel, SubmodelElement, SubmodelElementCollection
from basyx.aas.model import submodel as sm_model
from basyx.aas.adapter.aasx import AASXWriter, DictSupplementaryFileContainer

# --- SDK 심볼 (로컬 1.2.1 기준) ---

# Reference/Key/KeyTypes: base 우선, 없으면 reference 모듈 폴백

from basyx.aas.model.base import datatypes, AssetKind, ModellingKind, Resource
from basyx.aas.model.base import ModelReference, KeyTypes, Key, SpecificAssetId


# JSON/XML 직렬화
from basyx.aas.adapter.json import json_serialization as json_ser
from basyx.aas.adapter.xml import xml_serialization as xml_ser
from basyx.aas.adapter.xml import xml_deserialization as xml_des
from basyx.aas.adapter.json import json_deserialization as json_des


# AAS high-level
from basyx.aas.model.aas import AssetAdministrationShell, AssetInformation

# ---- DB모델경로 ----
from domain.models.aas import (
    DBAssetAdministrationShell, DBAssetInformation, DBSpecificAssetId, DBSubmodel, DBSubmodelElement,
    DBReference, DBReferenceKey, DBPropertyElement, DBRangeElement, DBFileElement,
    DBBlobElement, DBMultiLanguageProperty, DBSubModelElementCollection,
    DBReferenceElement, AASSubmodelReferences
)


class AASXHelper:
    """
    AAS id_short → BaSyx 객체 스토어 빌드(생성자에서 즉시) → (AASX/JSON/XML) 출력
    - AssetInformation: Optional (없어도 생성)
    - Enum 매핑: DB 값 UPPERCASE 전제 (INSTANCE/TYPE, INSTANCE/TEMPLATE)
    - defaultThumbnail(DBResource) → AASX 내부 경로 key로 매핑 + 실제 파일 포함 + 대표 썸네일 설정
    - Blob/File SME 포함
    """

    # 작은 File SME를 Blob으로 인라인하고 싶으면 >0
    INLINE_BLOB_MAX_BYTES = 0

    # ---------- 생성 / 상태 ----------
    def __init__(self, aas_id_short: str, include_descendants: bool = True):
        self.aas_id_short = aas_id_short
        self.obj_store: Optional[DictObjectStore] = None
        self.file_store: Optional[DictSupplementaryFileContainer] = None
        self.aas_ids: List[str] = []
        self.dic_aas_thumbnail = {}
        self.include_descendants = include_descendants  # ← 부모 AAS와 자식 AAS까지 한 패키지에 담을지
        self._visited_aas_ids = set()   


        self.db_file_elements =[]

        # 인스턴스 생성 시 바로 DB→스토어 빌드
        self.__build_stores__()

        return

    # ---------- DB → 스토어 (생성자에서 호출됨) ----------
    def __build_stores__(self):
        """
        ORM → (self.obj_store, self.file_store, self.aas_ids, thumb)
        """

        self.obj_store = DictObjectStore()
        self.file_store = DictSupplementaryFileContainer()
        self.aas_ids = []
        

        self._visited_aas_ids = set()

        aas  = DBAssetAdministrationShell.objects.select_related('AssetInformation', 'AssetInformation__defaultThumbnail').filter(id_short=self.aas_id_short).first()
        if not aas:
            raise Exception("aas not exist")

        root = (aas)
        self._add_aas_recursive(root)

        # 패키지에 포함할 AAS 목록:
        #  - 부모만: [root.id]
        #  - 부모+하위 모두: list(self._visited_aas_ids)
        self.aas_ids = list(self._visited_aas_ids if self.include_descendants else {root.id})

        return



    # ---------- AASX / JSON / XML ----------
    def write_aasx(self, out_path: str) -> None:

        if not self.obj_store:
            raise ValueError("AAS not found")
       
        try:
            with AASXWriter(out_path) as w:

                w.write_aas(aas_ids=self.aas_ids, object_store=self.obj_store, file_store=self.file_store, write_json=False)

                for thumb in self.dic_aas_thumbnail.values():
                    thumb_bytes, thumb_mime, path = thumb
                    w.write_thumbnail(path, thumb_bytes, thumb_mime)

        except Exception as ex:
            print(f"Failed to write AASX: {ex}")
            raise ex

    def to_file_response(self, download_filename: Optional[str] = None) -> FileResponse:

        if not self.obj_store:
            raise ValueError("AAS not found")
        
        aasx_directory = os.path.join(settings.AAS_BASE_PATH,"temp")
        if not os.path.exists(aasx_directory):
            os.makedirs(aasx_directory)

        filename = f"{uuid.uuid4()}.aasx"
        filepath = os.path.join(aasx_directory, filename)
        
        try:
            self.write_aasx(filepath)
            return FileResponse( open(filepath, "rb"), as_attachment=True, filename=download_filename or f"{self.aas_id_short}.aasx",  content_type="application/octet-stream")
        except Exception as ex:
            print(ex)
            raise ex


    def to_json_string(self, stripped: bool = False, **json_kwargs) -> str:
        if not self.obj_store:
            raise ValueError("AAS not found")
        return json_ser.object_store_to_json(self.obj_store, stripped=stripped, **json_kwargs)

    def to_xml_bytes(self, pretty_print: bool = True, xml_declaration: bool = True, encoding: str = "UTF-8") -> bytes:
        if not self.obj_store:
            raise ValueError("AAS not found")
        root_elem = xml_ser.object_store_to_xml_element(self.obj_store)
        return etree.tostring(root_elem, pretty_print=pretty_print, xml_declaration=xml_declaration, encoding=encoding)


    @staticmethod
    def _resolve_enum_member(enum_cls, name: Optional[str], prefer: tuple = ()) :
        """
        DB의 대문자 문자열을 SDK enum 멤버로 안전 변환.
        - 정확 속성명 시도 (원문, lower, upper, title)
        - 멤버 순회하며 m.name 대소문자 무시 비교
        - prefer 후보명 순서대로 시도
        - 그래도 없으면 enum의 첫 멤버 반환
        """
        if not enum_cls:
            raise ValueError("enum_cls is required")
        if not name:
            name = ""

        # 1) 속성으로 곧장
        for cand in (name, name.upper(), name.lower(), name.title()):
            if hasattr(enum_cls, cand):
                return getattr(enum_cls, cand)

        # 2) 멤버 순회 비교
        try:
            for m in enum_cls:
                if getattr(m, "name", "").upper() == name.upper():
                    return m
                # 일부 빌드는 value도 문자열일 수 있음
                if hasattr(m, "value") and str(m.value).upper() == name.upper():
                    return m
        except TypeError:
            # enum_cls가 iterable하지 않은 희귀 케이스
            pass

        # 3) 선호 후보
        for cand in prefer:
            if hasattr(enum_cls, cand):
                return getattr(enum_cls, cand)

        # 4) 최후: 첫 멤버
        try:
            return list(enum_cls)[0]
        except Exception:
            # 정말 예외적이면 그냥 enum 자체 반환(실패 방지)
            return enum_cls


    def _children_of(self, parent: DBAssetAdministrationShell) -> list[DBAssetAdministrationShell]:
        """
        parent(FK)로 부모를 가리키는 AAS들을 자식으로 간주.
        """
        return list(
            DBAssetAdministrationShell.objects
            .select_related('AssetInformation', 'AssetInformation__defaultThumbnail')
            .filter(parent=parent)  # ← FK가 parent를 가리킴
        )

    def _add_aas_recursive(self, db_aas: DBAssetAdministrationShell, parent:AssetAdministrationShell = None):

        if db_aas.id in self._visited_aas_ids:
            return

        aashell =  self._build_single_aas(db_aas)

        if parent:
            # 부모 AAS가 있다면 자식으로 추가
            aashell.parent =  parent.get_referable()


        # 자식 AAS가 있다면 재귀적으로 추가 --> 현재 AAS 하위에 자식 AAS가 있는 경우에 해당
        if self.include_descendants:
            for child in self._children_of(db_aas):
                self._add_aas_recursive(child, aashell)


    def get_specific_asset_ids(self, db_asset: DBAssetInformation) -> List[SpecificAssetId]:
        """
        특정 자산의 SpecificAssetId 목록을 반환.
        :param db_asset: DBAssetInformation 객체
        :return: SpecificAssetId 객체들의 리스트
        """
        specific_ids = []
        for sa in DBSpecificAssetId.objects.filter(AssetInformation=db_asset):
            specific_ids.append(SpecificAssetId(name=sa.name, value=sa.value))
        return specific_ids

    def _build_single_aas(self, db_aas: DBAssetAdministrationShell) -> AssetAdministrationShell:
        """
        단일 AAS(및 그 Submodel/SME, 썸네일 파일) → self.obj_store/self.file_store에 등록.
        반환: 생성된 AssetAdministrationShell 객체
        📌 주의: object_store에 넣는 대상
        AssetAdministrationShell
        Submodel
        ConceptDescription
        즉, 식별자(Identifier/str id_)를 가진 최상위 Identifiable 객체들만 object_store에 추가합니다.
        """
        # --- AssetInformation & 썸네일 ---
        db_asset_info = db_aas.AssetInformation

        asset_info_obj = None
        thumb_bytes = thumb_mime = None

        if db_asset_info:
            dt_res = None
            if db_asset_info.defaultThumbnail_id and db_asset_info.defaultThumbnail and db_asset_info.defaultThumbnail.path:

                # 내부 경로 (gid 포함) 생성
                # MIME은 DBResource.contentType 우선
                tmp_mime = db_asset_info.defaultThumbnail.contentType

                # asset Infomation에서 path는 상대경로 resource에서 path는물리적경로를 저장한다.
                thumb_bytes, thumb_mime = self._load_resource_file(db_asset_info.defaultThumbnail.path) # asset_infor.path 는 상대적 경로임                

                mime_final = tmp_mime or thumb_mime

                # file_store에 등록 (BytesIO!),  ai.defaultThumbnail.path-> 절대경로
                # db_asset_info.path 상대경로
                self.file_store.add_file(db_asset_info.path, BytesIO(thumb_bytes), mime_final)

                dt_res = Resource(path=db_asset_info.path, content_type=(mime_final or "image/png"))

                self.dic_aas_thumbnail[db_aas.id_short] = (thumb_bytes, thumb_mime, db_asset_info.path)

            asset_kind = self._resolve_enum_member(AssetKind, db_asset_info.assetKind, prefer=("INSTANCE","Instance","TYPE","Type"))
            specific_ids = self.get_specific_asset_ids(db_asset_info)

            # asset infomation
            asset_info_obj = AssetInformation(global_asset_id=db_asset_info.globalAssetId)
            asset_info_obj.asset_kind = asset_kind
            asset_info_obj.specific_asset_id=specific_ids
            asset_info_obj.asset_type=db_asset_info.assetType
            asset_info_obj.default_thumbnail = dt_res  # Resource 객체를 AssetInformation에 설정


        # submodels
        submodel_set = set()
        for db_submodel in self._resolve_submodels_via_refs(db_aas):
            submodel_obj = self._map_submodel(db_submodel)  # 내부에서 obj_store.add(sm)
            ref = ModelReference.from_referable(submodel_obj)
            submodel_set.add(ref)
            self.obj_store.add(submodel_obj)  # Submodel 객체를 스토어에 추가
        
        # --- AAS 설명 ---
        # --- AAS 본체 생성/등록 ---
        aashell = AssetAdministrationShell(asset_information=asset_info_obj, id_=db_aas.id, id_short=db_aas.id_short)
        aashell.category=db_aas.category
        aashell.display_name= MultiLanguageNameType({db_aas.language: db_aas.displayName})
        aashell.description=MultiLanguageTextType( {db_aas.language: db_aas.description} ) if db_aas.description else None
        aashell.submodel=submodel_set

        self.obj_store.add(aashell) #aas추가        

        # 방문 집합에 등록
        self._visited_aas_ids.add(aashell.id)

        return aashell



    @staticmethod
    def _to_abs_path(p: str) -> str:
        return p if os.path.isabs(p) else os.path.join(getattr(settings, "AAS_BASE_PATH", ""), p)


    def _load_resource_file(self, fs_path: str) -> Tuple[bytes, str]:

        with open(fs_path, "rb") as f:
            data = f.read()
        mime = mimetypes.guess_type(fs_path)[0] or "image/png"
        return data, mime

    # ---------- 유틸: 데이터 타입 ----------
    @staticmethod
    def _data_type_resolve(type_name: Optional[str]) -> datatypes.AnyXSDType:

        normalized = type_name.strip().lower()    

        # value→key 역방향 매핑
        reverse_map = {v.lower(): k for k, v in datatypes.XSD_TYPE_NAMES.items()}

        if normalized not in reverse_map:
            raise ValueError(f"Unknown XSD type name: {type_name}")

        return reverse_map[normalized]

    @staticmethod
    def get_keytype(value: str) -> KeyTypes:
        """
        문자열을 입력받아 KeyTypes enum 값을 반환한다.
        예: "AssetAdministrationShell" -> KeyTypes.ASSET_ADMINISTRATION_SHELL
        """
        if not value:
            raise ValueError("Empty string is not a valid KeyTypes name.")

        normalized = value.strip().upper()

        # Enum 멤버명 기반 매핑
        try:
            return KeyTypes[normalized]
        except KeyError:
            # Enum 값(value) 기반 매핑 시도 (예: "AssetAdministrationShell")
            for member in KeyTypes:
                if member.value.lower() == value.strip().lower():
                    return member
            raise ValueError(f"Unknown KeyTypes: {value}")



    # ---------- Reference ----------
    @staticmethod
    def _map_reference(db_ref: Optional[DBReference]) -> Optional[ModelReference]:
        if not db_ref:
            return None

        ktype = AASXHelper.get_keytype(db_ref.type)

        key = Key(ktype, db_ref.value)
        keys = (key,)

        model_reference= ModelReference(key=keys, type_=ktype)

        return model_reference

    # ---------- SME 매핑기들 ----------
    def _map_property(self, s: DBSubmodelElement) -> sm_model.Property:

        pe = DBPropertyElement.objects.filter(SubmodelElement=s).first()
        value_type=self._data_type_resolve(pe.valueType if pe else 'STRING')
        prpt = sm_model.Property(id_short=s.id_short, value=pe.value , value_type=value_type,)
        return prpt

    def _map_range(self, s: DBSubmodelElement) -> sm_model.Range:
        re = DBRangeElement.objects.filter(SubmodelElement=s).first()
        value_type = self._data_type_resolve(re.valueType if re else 'STRING')

        return sm_model.Range(
            id_short=s.id_short,
            value_type= value_type,
            min=(re.min if re else None),
            max=(re.max if re else None),
        )

    def _file_sme_to_blob_if_small(self, s: DBSubmodelElement) -> Optional[sm_model.Blob]:
        if not self.INLINE_BLOB_MAX_BYTES:
            return None

        db_file_element = DBFileElement.objects.filter(SubmodelElement=s).first()

        if not db_file_element or not db_file_element.value:
            return None
        
        if os.path.exists(db_file_element.path):
            with open(db_file_element.path, 'rb') as f:
                data = f.read()
            return sm_model.Blob(
                id_short=s.id_short,
                content_type=db_file_element.content_type or "application/octet-stream",
                value=data
            )
        return None


    def _map_file(self, s: DBSubmodelElement) -> sm_model.File:
        db_file_element = DBFileElement.objects.filter(SubmodelElement=s).first()        

        self.db_file_elements.append(db_file_element)  # DBFileElement 수집

        if db_file_element and db_file_element.value:
            fs_path = db_file_element.path
            if os.path.exists(fs_path):
                with open(fs_path, 'rb') as f:
                    data = f.read()
                mime = db_file_element.content_type or mimetypes.guess_type(fs_path)[0] or "application/octet-stream"
                self.file_store.add_file(db_file_element.value, BytesIO(data), mime)

        return sm_model.File(
            id_short=s.id_short,
            content_type=(db_file_element.content_type if db_file_element else "application/octet-stream"),
            value=db_file_element.value
        )

    def _map_blob(self, s: DBSubmodelElement) -> sm_model.Blob:
        be = DBBlobElement.objects.filter(SubmodelElement=s).first()
        return sm_model.Blob(
            id_short=s.id_short,
            content_type=(be.mimeType if be else "application/octet-stream"),
            value=(be.value if be and be.value else b"")
        )

    def _map_mlp(self, s: DBSubmodelElement) -> sm_model.MultiLanguageProperty:
        mlp = DBMultiLanguageProperty.objects.filter(SubmodelElement=s).first()
        lss = []
        if mlp and mlp.value:
            for item in mlp.value:
                lss.append(sm_model.LangString(name=item.get('text', ''), language=item.get('lang', 'en')))
        return sm_model.MultiLanguageProperty(id_short=s.id_short, value=sm_model.LangStringSet(lss))

    def _map_reference_element(self, s: DBSubmodelElement) -> sm_model.ReferenceElement:
        re = DBReferenceElement.objects.filter(SubmodelElement=s).first()
        return sm_model.ReferenceElement(
            id_short=s.id_short,
            value=self._map_reference(re.value) if re else None
        )

    def _map_smc(self, s: DBSubmodelElement) -> sm_model.SubmodelElementCollection:
        smc_rec = DBSubModelElementCollection.objects.filter(sme_pk=s.pk).first()
        children = []
        if smc_rec:
            for child in smc_rec.values.all():
                children.append(self._map_sme(child))
        return sm_model.SubmodelElementCollection(id_short=s.id_short, value=children)



    def _map_sme(self, s: DBSubmodelElement):
        t = (s.modelType or '').upper()

        try:

            if t == 'PROPERTY':
                return self._map_property(s)
            if t == 'RANGE':
                return self._map_range(s)
            if t == 'FILE':
                alt = self._file_sme_to_blob_if_small(s)
                return alt if alt else self._map_file(s)
            if t == 'BLOB':
                return self._map_blob(s)
            if t in ('MLP', 'MULTILANGUAGEPROPERTY'):
                return self._map_mlp(s)
            if t in ('COLLECTION', 'SUBMODELELEMENTCOLLECTION', 'SMC'):
                return self._map_smc(s)
            if t in ('REFERENCE', 'REFERENCE ELEMENT', 'REFERENCEELEMENT'):
                return self._map_reference_element(s)

            # 위의 경우가 벗어 나면 Property로 간주
            prpt = sm_model.Property(id_short=s.id_short or 'Unknown', value='', value_type=self._data_type_resolve('STRING'))
            return prpt
        except Exception as ex:
            print(f"Failed to map SubmodelElement {s.id_short}, t:{t} : {ex}")
            raise ex

    # ---------- Submodel ----------
    def _map_submodel(self, db_sm: DBSubmodel) -> sm_model.Submodel:
        # DB 값이 'INSTANCE'/'TEMPLATE'라고 가정
        kind = getattr(ModellingKind, db_sm.kind or 'INSTANCE', ModellingKind.INSTANCE)
        semantic_id = self._map_reference(db_sm.semanticId)

        # submodel_element 매핑
        smes_qs = DBSubmodelElement.objects.filter(Submodel=db_sm)
        submodel_element_objects = None

        try:
            submodel_element_objects = [self._map_sme(s) for s in smes_qs]
        except Exception as ex:
            raise ex


        submodel_obj = sm_model.Submodel( id_=db_sm.id, id_short=db_sm.id_short)
        submodel_obj.display_name= MultiLanguageNameType({db_sm.language: db_sm.displayName})
        submodel_obj.description=MultiLanguageTextType({db_sm.language: db_sm.description})
        submodel_obj.kind=kind
        submodel_obj.category=db_sm.category or None
        submodel_obj.semantic_id=semantic_id
        submodel_obj.submodel_element=submodel_element_objects
        
        return submodel_obj
    

    # ---------- AAS ↔ Submodel 연결 ----------
    @staticmethod
    def _resolve_submodels_via_refs(db_aas: DBAssetAdministrationShell) -> List[DBSubmodel]:
        """
        AASSubmodelReferences.reference → DBReferenceKey(type='SUBMODEL').value == DBSubmodel.id
        """
        result: List[DBSubmodel] = []
        links = AASSubmodelReferences.objects.select_related('reference').filter(aas=db_aas)
        for link in links:
            ref = link.reference
            for k in DBReferenceKey.objects.filter(Reference=ref, type='SUBMODEL'):
                try:
                    result.append(DBSubmodel.objects.get(id=k.value))
                except DBSubmodel.DoesNotExist:
                    raise ValueError(f"DBReferenceKey - Submodel with id {k.value} not found for AAS {db_aas.id_short}")
        return result




class AASXImporter:
    """
    AASX(.zip) 패키지를 열어 AAS/서브모델/요소/리소스를 DB에 저장하는 Import 서비스.
    - BaSyx 1.2.1 가정
    - XML 우선 (write_json=False로 만든 AASX가 가장 호환성 좋음)
    - JSON(data.json)도 있으면 파싱 시도
    """

    def __init__(self, media_root: str):
        """
        media_root: 리소스 파일을 보관할 루트 디렉터리 (예: '/srv/resources')
        """
        self.media_root = Path(media_root)

        # BaSyx ObjectStore: 역직렬화 중 임시로 담아 전체 그래프를 순회
        self.obj_store = DictObjectStore()

    # --------------- 공개 API ---------------
    def import_aasx(self, aasx_path: str) -> None:
        """
        AASX 파일 하나를 열어 DB에 반영(업서트).
        """
        with zipfile.ZipFile(aasx_path, "r") as zf:
            members = set(zf.namelist())

            # 1) 환경(XML/JSON) 읽기
            # - XML 경로 패턴: 'aasx/aas/*.xml', 'aasx/submodels/*.xml'
            # - JSON 경로: 'aasx/data.json' (주의: 0byte일 수 있음 → 무시)
            xml_paths = sorted([m for m in members if m.endswith(".xml") and ("/aas/" in m or "/submodels/" in m)])
            data_json = "aasx/data.json" if "aasx/data.json" in members else None

            parsed = False
            if xml_paths:
                for p in xml_paths:
                    self._parse_xml_into_store(zf, p)
                parsed = True
            elif data_json:
                self._parse_json_into_store(zf, data_json)
                parsed = True

            if not parsed:
                raise ValueError("AASX 안에서 파싱 가능한 XML/JSON 환경을 찾지 못했습니다.")

            # 2) 리소스 복사 (resources/**)
            self._extract_resources(zf, members)

        # 3) ObjectStore → DB 반영
        self._store_to_db()

    # --------------- 내부: 파싱 ---------------
    def _parse_xml_into_store(self, zf: zipfile.ZipFile, member: str) -> None:
        """
        개별 XML (AAS/서브모델)을 ObjectStore로 역직렬화.
        1.2.1에서는 xml_deserialization 쪽 API가 버전에 따라 다를 수 있어
        파일 핸들 → 문자열 → file-like 로 안전하게 주입합니다.
        """
        data = zf.read(member)
        bio = io.BytesIO(data)

        # 가능한 함수 시그니처에 적응 (버전에 따라 다름)
        # 1) read_aas_xml / read_aas_xml_file 계열
        if hasattr(xml_des, "read_aas_xml_file"):
            # 일부 버전: (path_or_file, object_store) 형태
            xml_des.read_aas_xml_file(bio, self.obj_store)
            return
        if hasattr(xml_des, "read_aas_xml"):
            # 일부 버전: (file_like) → Environment/Store 반환 or 내부 전개
            try:
                env = xml_des.read_aas_xml(bio)
                # env 가 ObjectStore 또는 Environment일 수 있음 → store에 삽입
                self._merge_env_into_store(env)
                return
            except TypeError:
                # (file_like, object_store) 시그니처일 수도 있음
                xml_des.read_aas_xml(bio, self.obj_store)
                return

        # 2) 마지막 수단: BaSyx가 제공하는 다른 헬퍼 함수가 있다면 여기에 추가
        raise RuntimeError("xml_deserialization API가 이 버전에서 예상과 달라 XML 파싱 실패.")

    def _parse_json_into_store(self, zf: zipfile.ZipFile, member: str) -> None:
        """
        data.json → ObjectStore로 역직렬화 (0 byte면 스킵)
        """
        data = zf.read(member)
        if not data:
            # 빈 JSON이면 무시
            return

        bio = io.BytesIO(data)
        # 마찬가지로 버전별 시그니처 호환
        if hasattr(json_des, "read_aas_json_file"):
            json_des.read_aas_json_file(bio, self.obj_store)
            return
        if hasattr(json_des, "read_aas_json"):
            try:
                env = json_des.read_aas_json(bio)
                self._merge_env_into_store(env)
                return
            except TypeError:
                json_des.read_aas_json(bio, self.obj_store)
                return

        raise RuntimeError("json_deserialization API가 이 버전에서 예상과 달라 JSON 파싱 실패.")

    def _merge_env_into_store(self, env_obj) -> None:
        """
        xml/json 역직렬화가 Environment나 Store를 돌려줄 때, DictObjectStore로 내용 병합.
        """
        # 가장 보수적으로: env_obj가 iterable(Identifiable들)이라고 가정하고 add
        try:
            for ident in env_obj:
                self.obj_store.add(ident)
        except Exception:
            # 필요하면 여기서 env_obj.asset_administration_shells 등 속성을 순회
            # (버전차 방어)
            for ident in getattr(env_obj, "asset_administration_shells", []) or []:
                self.obj_store.add(ident)
            for ident in getattr(env_obj, "submodels", []) or []:
                self.obj_store.add(ident)
            for ident in getattr(env_obj, "concept_descriptions", []) or []:
                self.obj_store.add(ident)

    # --------------- 내부: 리소스 추출 ---------------
    def _extract_resources(self, zf: zipfile.ZipFile, members: set[str]) -> None:
        """
        AASX 내부 리소스('/resources/**' 또는 'resources/**')를 media_root로 복사.
        DB에는 나중에 value='/resources/..' 로 저장하고, path는 실제 파일 경로로 저장.
        """
        res_like = [m for m in members if m.replace("\\", "/").lower().endswith((".png", ".jpg", ".jpeg", ".pdf", ".txt", ".bin"))]
        for m in res_like:
            norm = m.replace("\\", "/")
            # ZIP 내 키가 'resources/..' 또는 '/resources/..' 모두 수용
            if "resources/" not in norm:
                continue
            rel = "/" + norm.split("resources/", 1)[1]      # → '/thumbnails/..' or '/fe_..'
            out_rel = "/resources/" + rel.lstrip("/")       # 항상 '/resources/..'로 정규화
            target = self.media_root.joinpath(out_rel.lstrip("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as f:
                f.write(zf.read(m))
        # 썸네일/파일 DB 반영은 _store_to_db() 단계에서 수행

    # --------------- 내부: ObjectStore → DB ---------------
    def _store_to_db(self) -> None:
        """
        ObjectStore에 들어있는 Identifiable들을 순회하여 DB에 업서트.
        - AAS
        - Submodel
        - SubmodelElement (Property/File/Collection 등)
        - AssetInformation(DefaultThumbnail) & 리소스 파일 매핑
        """

        # 1) AAS들
        for obj in self.obj_store:
            if isinstance(obj, AssetAdministrationShell):
                self._upsert_aas(obj)

        # 2) Submodel들
        for obj in self.obj_store:
            if isinstance(obj, Submodel):
                self._upsert_submodel(obj)

    # -------- AAS 저장 --------
    def _upsert_aas(self, aas: AssetAdministrationShell) -> None:
        # (예시) Django ORM 업서트
        # row, _ = DBAssetAdministrationShell.objects.update_or_create(
        #     id=aas.id,
        #     defaults=dict(
        #         id_short = aas.id_short or "",
        #         category = aas.category or "",
        #         display_name = self._mln_to_dict(aas.display_name),
        #         description = self._mlt_to_dict(aas.description),
        #         # parent/derived_from 등 필요시 추가
        #     )
        # )

        # 썸네일이 있으면 DBFileElement(or 별도 Thumbnail 테이블)에 저장
        if aas.asset_information and aas.asset_information.default_thumbnail:
            res = aas.asset_information.default_thumbnail
            # 모델은 '/resources/..' 로 들어있을 확률 ↑
            zip_uri = self._model_uri(res.path)
            abs_path = str(self.media_root.joinpath(zip_uri.lstrip("/")))
            mime = getattr(res, "content_type", None) or "application/octet-stream"
            # DB에 반영
            # DBFileElement.objects.update_or_create(
            #     aas_id=row.id, kind="thumbnail",
            #     value=zip_uri, path=abs_path, mime=mime
            # )

        # AAS → Submodel 참조는 DB 레이어에서 관계 테이블로 저장
        for ref in (aas.submodel or []):
            k = ref.key[0]
            if k.type == KeyTypes.SUBMODEL:
                sm_id = k.value
                # 예) AAS_Submodel_Rel.objects.update_or_create(aas_id=row.id, submodel_id=sm_id)
                pass

    # -------- Submodel 저장 --------
    def _upsert_submodel(self, sm: Submodel) -> None:
        # row, _ = DBSubmodel.objects.update_or_create(
        #     id=sm.id,
        #     defaults=dict(
        #         id_short = sm.id_short or "",
        #         category = sm.category or "",
        #         kind     = getattr(sm, "kind", None).value if getattr(sm, "kind", None) else "Instance",
        #         display_name = self._mln_to_dict(sm.display_name),
        #         description  = self._mlt_to_dict(sm.description),
        #     )
        # )
        # SubmodelElements 순회
        for sme in (sm.submodel_element or []):
            self._upsert_sme(sm.id, sme)

    # -------- SME 저장 (Property / File / Collection) --------
    def _upsert_sme(self, submodel_id: str, sme: SubmodelElement) -> None:
        if isinstance(sme, sm_model.Property):
            # DBProperty.objects.update_or_create(
            #     submodel_id=submodel_id, id_short=sme.id_short,
            #     defaults=dict(
            #         value=self._val_to_str(sme.value),
            #         value_type=self._xsd_to_string(sme.value_type),
            #         category=sme.category or "",
            #     )
            # )
            return

        if isinstance(sme, File):
            # 모델 값은 '/resources/..' 여야 함
            zip_uri = self._model_uri(sme.value)
            abs_path = str(self.media_root.joinpath(zip_uri.lstrip("/")))
            mime = getattr(sme, "content_type", None) or "application/octet-stream"
            # DBFileElement.objects.update_or_create(
            #     submodel_id=submodel_id, id_short=sme.id_short,
            #     defaults=dict(value=zip_uri, path=abs_path, mime=mime)
            # )
            return

        if isinstance(sme, SubmodelElementCollection):
            for child in (sme.value or []):
                self._upsert_sme(submodel_id, child)
            return

        # TODO: 필요 시 다른 SME 타입들(Blob, Range, MultiLanguageProperty 등) 추가

    # --------------- 유틸 ---------------
    def _mln_to_dict(self, mln: Optional[Any]) -> dict[str, str]:
        """
        display_name → {'ko-KR': '텍스트', ...}
        - BaSyx 1.2.1의 MultiLanguageNameType(=dict-like) 우선 처리
        - 혹시 (language, text) 튜플 리스트나 LangString* 객체 리스트가 와도 호환
        """
        if not mln:
            return {}

        # dict-like (MultiLanguageNameType 포함)
        if hasattr(mln, "items"):
            return {str(k): str(v) for k, v in mln.items() if k and v is not None}

        out: dict[str, str] = {}
        # (language, text) 튜플/리스트 형태
        try:
            for item in mln:  # type: ignore
                if isinstance(item, tuple) and len(item) == 2:
                    lang, txt = item
                    if lang and txt is not None:
                        out[str(lang)] = str(txt)
                    continue
                # LangString* 객체 형태(language, text 속성) 호환
                lang = getattr(item, "language", None) or getattr(item, "lang", None)
                txt = getattr(item, "text", None)
                if lang and txt is not None:
                    out[str(lang)] = str(txt)
        except TypeError:
            pass

        return out


    def _mlt_to_dict(self, mlt: Optional[Any]) -> dict[str, str]:
        """
        description → {'ko-KR': '텍스트', ...}
        - BaSyx 1.2.1의 MultiLanguageTextType(=dict-like) 우선 처리
        - (language, text) 튜플 리스트나 LangString* 객체 리스트도 호환
        """
        if not mlt:
            return {}

        if hasattr(mlt, "items"):
            return {str(k): str(v) for k, v in mlt.items() if k and v is not None}

        out: dict[str, str] = {}
        try:
            for item in mlt:  # type: ignore
                if isinstance(item, tuple) and len(item) == 2:
                    lang, txt = item
                    if lang and txt is not None:
                        out[str(lang)] = str(txt)
                    continue
                lang = getattr(item, "language", None) or getattr(item, "lang", None)
                txt = getattr(item, "text", None)
                if lang and txt is not None:
                    out[str(lang)] = str(txt)
        except TypeError:
            pass

        return out

    def _xsd_to_string(self, vt) -> str:
        """
        Property.value_type → 'xs:string' 같은 문자열로 역변환.
        (1.2.1의 datatypes.XSD_TYPE_NAMES를 이용)
        """
        # vt가 타입(예: datatypes.String)일 수도 있고, 문자열일 수도 있음.
        if isinstance(vt, str):
            return vt
        # 타입이면 역매핑
        for k, v in datatypes.XSD_TYPE_NAMES.items():
            if k is vt:
                return v  # 예: 'xs:string'
        # fallback
        return "xs:string"

    def _val_to_str(self, v) -> Optional[str]:
        """Property.value → DB 저장용 문자열"""
        if v is None:
            return None
        return str(v)

    def _model_uri(self, p: str) -> str:
        """모델에 쓰이는 URI path 규격 유지: 항상 선행 '/' 있고, 끝 '/' 없음."""
        if not p:
            return "/"
        s = str(p).replace("\\", "/").strip()
        if not s.startswith("/"):
            s = "/" + s
        if s != "/" and s.endswith("/"):
            s = s[:-1]
        return s


