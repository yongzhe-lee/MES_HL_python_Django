from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from configurations import settings

class BOMService():
    def __init__(self):
        pass

    def get_bom_list(self, mat_type, mat_group, bom_type, mat_name, not_past_flag='Y'):
        """ BOM header 목록
            not_past_flag : 과거데이터 제외 if 'Y'
        """
        sql = ''' 
        WITH A AS (
            SELECT 
                b.id
                , b."Name"
                , b."BOMType"
                , fn_code_name('bom_type', b."BOMType") AS bom_type_name
                , b."OutputAmount"
                , b."Version"
                , to_char(b."StartDate", 'yyyy-mm-dd') AS "StartDate"
                , to_char(b."EndDate", 'yyyy-mm-dd') AS "EndDate"
                , b."Material_id"
                , m."Name" AS mat_name
                , m."Code" AS mat_code
                , mg."Name" AS mat_group_name
                , fn_code_name('mat_type', mg."MaterialType") AS mat_type
                , u."Name" AS unit
                , ROW_NUMBER() OVER (
                    PARTITION BY b."BOMType", b."Material_id" ORDER BY b."StartDate" desc
                    ) AS g_idx
                , CASE 
                    WHEN TO_CHAR(current_date, 'yyyy-mm-dd') BETWEEN TO_CHAR(b."StartDate", 'yyyy-mm-dd') AND TO_CHAR(b."EndDate", 'yyyy-mm-dd') THEN 'current'
                    WHEN b."StartDate" IS NULL OR b."EndDate" IS NULL THEN 'error'
                    WHEN TO_CHAR(current_date, 'yyyy-mm-dd') > TO_CHAR(b."EndDate", 'yyyy-mm-dd') THEN 'past' 
                    WHEN TO_CHAR(current_date, 'yyyy-mm-dd') < TO_CHAR(b."StartDate", 'yyyy-mm-dd') THEN 'future'
                    ELSE 'error' 
                    END AS current_flag
            FROM bom b 
            LEFT JOIN material m ON b."Material_id" = m.id 
            LEFT JOIN unit u ON u.id = m."Unit_id"
            LEFT JOIN mat_grp mg ON mg.id=m."MaterialGroup_id" 
            WHERE 1=1
        '''
        if mat_type:
            sql+=''' AND mg."MaterialType" = %(mat_type)s
            '''

        if mat_group:
            sql+='''AND m."MaterialGroup_id" = %(mat_group)s
            '''
        if bom_type:
            sql+=''' AND b."BOMType" = %(bom_type)s
            '''
        if mat_name:
            sql+=''' AND (m."Code" LIKE CONCAT('%%',%(mat_name)s,'%%') OR m."Name" LIKE CONCAT('%%',%(mat_name)s,'%%') )
            '''
        sql += ''' )
        SELECT *
        FROM A
        '''
        if not_past_flag == 'Y':
            sql += ''' WHERE ( A.current_flag IN ( 'current','future') OR A.g_idx = 1 ) '''
        sql += ''' ORDER BY A.mat_group_name, A.mat_code, A.mat_name , A."Material_id", A.bom_type_name
        '''
        try:
            dc = { }
            dc['mat_type'] = mat_type
            dc['mat_group'] = mat_group
            dc['bom_type'] = bom_type
            dc['mat_name'] = mat_name
            items = DbUtil.get_rows(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error', 'BOMService.get_bom_list', ex)
            raise ex

        return items
    

    def get_bom_detail(self, bom_id):

        result = {}
        sql = '''
        SELECT 
            b.id
            , b."Name"
            , b."BOMType"
            , b."OutputAmount"
            , b."Version"
            , to_char(b."StartDate", 'yyyy-mm-dd') AS "StartDate"
            , to_char(b."EndDate", 'yyyy-mm-dd') AS "EndDate"
            , b."Material_id"
            , m."Name" AS "MaterialName"
            , m."Code" AS mat_code
            , mg."Name" AS mat_group_name
            , fn_code_name('mat_type', mg."MaterialType") AS mat_type
        FROM bom b 
        LEFT JOIN material m ON b."Material_id" = m.id 
        LEFT JOIN mat_grp mg ON mg.id = m."MaterialGroup_id"
        WHERE b.id=%(id)s
        '''
        try:
            items = DbUtil.get_row(sql, {'id':bom_id})

        except Exception as ex:
            LogWriter.add_dblog('error', 'BOMService.get_bom_detail', ex)
            raise ex

        return items

    def get_bom_material_list(self, bom_id):
        items = []
        dic_param = {'bom_id':bom_id}
        sql = '''
        SELECT 
            bc.id
            , fn_code_name('mat_type', mg."MaterialType") AS mat_type
            , mg."Name" AS group_name
            , m."Name" AS mat_name
            , m."Code" AS mat_code
            , bc."Amount"
            , bc."Material_id" AS mat_id
            , m."Unit_id"
            , u."Name" AS unit
            , bc."Description"
            , bc."_order" 
        FROM bom_comp bc
        LEFT JOIN material m ON bc."Material_id"=m.id
        LEFT JOIN unit u ON u.id = m."Unit_id" 
        LEFT JOIN mat_grp mg ON m."MaterialGroup_id" =mg.id
        WHERE bc."BOM_id" = %(bom_id)s
        ORDER BY bc."_order"
        '''
        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error', 'BOMService.get_bom_material_list', ex)
            raise ex

        return items

    def get_bom_material_tree_list(self, id):
        sql = '''
        WITH RECURSIVE bom_tree AS 
        (
            WITH bom AS (
                SELECT 
                    b1.id AS bom_pk
                    , b1."Name"
                    , b1."Material_id" AS prod_pk
                    , NULLIF(b1."OutputAmount",0) AS produced_qty
                    , ROW_NUMBER() OVER(PARTITION BY b1."Material_id" ORDER BY b1."StartDate" DESC) AS g_idx
                FROM bom b1
                INNER JOIN bom b on b1."BOMType" = b."BOMType"
                WHERE b.id = %(id)s
                )
            SELECT 
                1 AS lvl
                , bc."Material_id"
                , bc._order::INTEGER AS item_order
                , bc."Material_id" AS parent_mat_id
                , bc."Amount" AS quantity
                , bom.produced_qty 
                , bc."Amount" / bom.produced_qty AS bom_ratio
                , bc."Description"
                , 'base' AS data_div
                , bc.id AS bc_id
                , LPAD(bc._order::TEXT, 4, '0') AS tot_order
                , bc."Material_id"::TEXT AS my_key
                , '' AS parent_key
            FROM bom_comp bc
            INNER JOIN bom ON bom.bom_pk = bc."BOM_id"
            WHERE bc."BOM_id" = %(id)s
            UNION ALL
            SELECT 
                bom_tree.lvl + 1 AS lvl
                , bc."Material_id"
                , bc._order::INTEGER AS item_order
                , bom_tree."Material_id" AS parent_mat_id
                , bc."Amount" AS quantity
                --, (bom_tree.quantity * bc."Amount" / bom.produced_qty)::NUMERIC(10,2) AS produced_qty
                , bom.produced_qty 
                , bc."Amount" / bom.produced_qty * bom_tree.bom_ratio AS bom_ratio
                , bc."Description"
                , 'child' AS data_div
                , bc.id AS bc_id
                , bom_tree.tot_order ||'-'||LPAD(bc._order::text, 4, '0') AS tot_order
                , bom_tree.my_key ||'-'||bc."Material_id"::TEXT AS my_key
                , bom_tree.my_key AS parent_key
            FROM bom_tree 
            INNER JOIN bom ON bom.prod_pk = bom_tree."Material_id"
            INNER JOIN bom_comp bc ON bc."BOM_id" = bom.bom_pk
            WHERE 1=1
            AND bom.g_idx = 1
        )
        SELECT 
            bom_tree.lvl
            , bom_tree.my_key
            , CASE WHEN bom_tree.data_div = 'child' THEN bom_tree.parent_key END AS parent_key
            , bom_tree."Material_id" AS mat_id
            , CASE WHEN bom_tree.data_div = 'child' THEN bom_tree.parent_mat_id END AS parent_mat_id
            , fn_code_name('mat_type', mg."MaterialType") AS mat_type
            , m."Name" AS mat_name
            , m."Code" AS mat_code
            , bom_tree.quantity
            , bom_tree.produced_qty
            , bom_tree.bom_ratio::NUMERIC(15,7)
            , CONCAT(bom_tree.quantity::DECIMAL,'/', bom_tree.produced_qty::DECIMAL) AS bom_qty
            , u."Name" AS unit
            , bom_tree."Description"
            , bom_tree.bc_id
            , bom_tree.tot_order
        FROM bom_tree 
        INNER JOIN material m ON m.id = bom_tree."Material_id"
        LEFT JOIN unit u ON u.id = m."Unit_id" 
        LEFT JOIN mat_grp mg ON m."MaterialGroup_id"=mg.id
        ORDER BY bom_tree.tot_order ASC
        '''
        try:
            items = DbUtil.get_rows(sql, {'id':id})
        except Exception as ex:
            LogWriter.add_dblog('error', 'BOMService.get_bom_material_tree_list', ex)
            raise ex

        return items


    def get_bom_material_detail(self, id):
        sql = '''
        SELECT bc.id
            , bc."BOM_id"
            , fn_code_name('mat_type', mg."MaterialType") AS mat_type
            , mg."Name" AS group_name
            , m."Name" AS "MaterialName"
            , m."Code" AS mat_code
            , bc."Amount"
            , bc."Material_id"
            , m."Unit_id"
            , u."Name" AS unit
            , bc."Description"
            , bc."_order"
            , bom."Name" AS bom_name
            , pm."Name" AS "ParentMaterialName"
            , bom."Material_id" AS "ParentMaterial_id"
        FROM bom_comp bc
        INNER JOIN bom ON bom.id=bc."BOM_id"
        LEFT JOIN material m ON bc."Material_id"=m.id
        LEFT JOIN material pm ON bom."Material_id"=pm.id
        LEFT JOIN unit u ON u.id = m."Unit_id" 
        LEFT JOIN mat_grp mg ON m."MaterialGroup_id" =mg.id
        WHERE bc.id = %(id)s
        '''

        try:
            items = DbUtil.get_row(sql, {'id':id})

        except Exception as ex:
            LogWriter.add_dblog('error', 'BOMService.get_bom_list', ex)
            raise ex

        return items


    def bom_duplicate_check(self, bom_id, material_id, start_date, end_date, bom_type):

        sql = '''
        SELECT COUNT(*) AS cnt 
        FROM bom 
        WHERE "Material_id" = %(Material_id)s
            AND "BOMType" = %(bom_type)s
            AND "StartDate" <= %(end_date)s 
            AND "EndDate" >= %(start_date)s 
        '''
        if bom_id:
            sql += ''' AND id <> %(bom_id)s
            '''
        
        result = False
        try:
            dc = {
                'Material_id' : material_id,
                'start_date':start_date, 
                'end_date':end_date, 
                'bom_type':bom_type,
                'bom_id':bom_id
            }
            row = DbUtil.get_row(sql, dc)
            if row.get('cnt') > 0:
                result = True

        except Exception as ex:
            source =  'BOMService.duplicate_check'
            LogWriter.add_dblog('error', source, ex)
            raise ex

        return result


    def get_bom_all_list(self, bom_type):
        """  엑셀파일에 모든 BOM 한꺼번에 출력하는 용도
        """
        sql = ''' 
        SELECT 
            b.id AS bom_id
            , b."BOMType" 
            , fn_code_name('mat_type', mg2."MaterialType") AS bom_mat_type
            ,  mg2."Name" AS bom_mat_group_name
            , m2."Code" AS bom_mat_code
            , m2."Name" AS bom_mat_name			
            , b."Name" AS bom_name
            , b."Version"
            , b."OutputAmount" 
            , u2."Name" AS bom_mat_unit
            , TO_CHAR(b."StartDate",'yyyy-mm-dd') AS "StartDate"
            , TO_CHAR(b."EndDate",'yyyy-mm-dd') AS "EndDate"
            , bc.id
            , fn_code_name('mat_type', mg."MaterialType") AS mat_type
            ,  mg."Name" AS group_name
            ,  m."Name" AS mat_name
            ,  m."Code" AS mat_code
            ,  bc."Amount"
            ,  u."Name" AS unit
            ,  bc."Material_id"
            ,  m."Unit_id"
            ,  bc."_order"           
        FROM bom b
        INNER JOIN material m2 ON m2.id = b."Material_id" 
        LEFT JOIN mat_grp mg2 ON m2."MaterialGroup_id" = mg2.id
        LEFT JOIN unit u2 ON u2.id = m2."Unit_id" 
        LEFT JOIN bom_comp bc ON b.id = bc."BOM_id" 
        LEFT JOIN material m ON bc."Material_id"= m.id
        LEFT JOIN unit u ON u.id = m."Unit_id" 
        LEFT JOIN mat_grp mg ON m."MaterialGroup_id" = mg.id
        WHERE 1 = 1 
        '''
        if bom_type:
            sql += ''' AND b."BOMType" = %(bom_type)s
            '''
        sql += ''' 
        AND ( current_date BETWEEN b."StartDate" AND b."EndDate" 
            OR current_date < b."StartDate")
        ORDER BY 3,4,5,6, b."StartDate" DESC, b.id ,bc."_order"
        '''
        try:
            dc = {}
            dc['bom_type'] = bom_type
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'BOMService.get_bom_all_list', ex)
            raise ex

        return items


    def is_safe_child(self, bom_pk, mat_pk):
        """ 추가하려고 하는 자식들 중 부모가 속해 있는지 체크.무한루프 방지 위해 필요.
        """
        sql = '''	
        WITH A AS (
	        SELECT "Material_id" AS mat_pk 
	        FROM "bom" b 
	        WHERE id = %(bom_pk)s
	    )
	    SELECT COUNT(*) AS cnt
	    FROM A 
	    LEFT JOIN tbl_bom_detail(%(mat_pk)s, TO_CHAR(NOW(),'yyyy-mm-dd')) B ON 1 = 1
	    WHERE A.mat_pk IN (B.mat_pk, %(mat_pk)s )
        '''
        dc = {}
        dc['bom_pk'] = bom_pk 
        dc['mat_pk'] = str(mat_pk )

        row =  DbUtil.get_row(sql, dc)

        if row['cnt'] == 0:
            return True

        return False


