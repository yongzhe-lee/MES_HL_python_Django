// kendo ui file upload 컴포넌트를 사용하기 위한 클래스.
class FileUpload {
    constructor($target, options) {
        this.init($target, options);
    }

    init($target, options) {
        let defaultOptions = {
            async: {
                autoUpload: true, // 파일을 선택하자마자 자동으로 업로드할지 여부.
                batch: false, // 여러 파일을 하나의 요청으로 묶어서 전송할지 여부.
                removeField: "fileNames", // 서버에서 파일을 제거할 때 사용할 필드명.
                removeUrl: '/api/files/upload?action=remove_file', // 파일을 제거하기 위해 요청을 보낼 URL.
                saveField: "uploadfile", // 파일을 업로드할 때 사용할 필드명.
                saveUrl: '/api/files/upload?action=save_file' // 파일을 저장하기 위해 요청을 보낼 URL.
            },
            directory: false, // 디렉토리 업로드를 허용할지 여부.
            directoryDrop: false, // 드롭 영역에 디렉토리를 끌어다 놓을 수 있는지 여부.
            dropZone: null, // 파일을 드래그하여 놓을 수 있는 영역.
            enabled: true, // 업로드 컴포넌트를 활성화할지 여부.
            files: [], // 초기에 설정된 파일 목록.
            localization: {
                cancel: "취소", // 취소 버튼의 텍스트
                clearSelectedFiles: "선택 해제", // 선택된 파일 목록을 클리어하는 버튼의 텍스트
                dropFilesHere: "여기에 파일을 드랍하세요", // 드롭존에 파일을 떨어뜨렸을 때 표시할 메시지
                headerStatusUploaded: "완료", // 파일 업로드가 완료되었을 때 헤더 상태 메시지
                headerStatusUploading: "업로드 중...", // 파일 업로드 중일 때 헤더 상태 메시지
                invalidFileExtension: "허용되지 않는 파일 형식입니다.", // 허용되지 않는 파일 확장자를 업로드하려 할 때의 메시지
                invalidFiles: "유효하지 않은 파일이 발견되었습니다.", // 유효하지 않은 파일을 업로드하려 할 때의 메시지
                invalidMaxFileSize: "파일 크기가 너무 큽니다.", // 파일 크기가 설정된 최대값을 초과할 때의 메시지
                invalidMinFileSize: "파일 크기가 너무 작습니다.", // 파일 크기가 설정된 최소값보다 작을 때의 메시지
                remove: "제거", // 파일 제거 버튼의 텍스트
                retry: "재시도", // 업로드 실패 후 재시도 버튼의 텍스트
                select: "파일 선택...", // 파일 선택 버튼의 텍스트
                statusFailed: "실패", // 파일 업로드 실패 시 상태 메시지
                statusUploaded: "업로드 완료", // 파일이 성공적으로 업로드되었을 때의 상태 메시지
                statusUploading: "업로드 중", // 파일이 업로드 중일 때의 상태 메시지
                uploadSelectedFiles: "선택된 파일 업로드" // 선택된 파일을 업로드하는 버튼의 텍스트
            },
            multiple: true, // 여러 파일을 한 번에 선택할 수 있는지 여부.
            showFileList: true, // 파일 목록을 표시할지 여부.
            template: function (e) { // 파일 목록을 커스텀하게 표시하기 위한 템플릿.
                return "<span class='k-progress'></span>" +
                    "<div class='file-wrapper'>" +
                    "<h4 class='file-heading file-name-heading'>" + e.name + "</h4>" +
                    "<button type='button' id='" + e.files[0].uid + "' class='btn-file-download' data-fileId=''><span class='material-symbols-outlined'>download</span ></button>" +
                    "<button type='button' class='k-upload-action'></button>" +
                    "</div>";
            },
            validation: {
                allowedExtensions: [], // 허용하는 파일 확장자 목록.
                maxFileSize: 4194304, // 허용하는 최대 파일 크기.
                minFileSize: 0 // 허용하는 최소 파일 크기.
            },
            select: function (e) {
                console.log('select e', e);
            },
            success: function (e) {
                console.log('success e', e);
                $('#' + e.files[0].uid).data("fileId", e.response.fileId);
                $('#' + e.files[0].uid).on('click', function () {
                    let $this = $(this);
                    AjaxUtil.downloadFile('/api/files/download?file_id=' + $this.data('fileId'), e.response.fileNm);
                });
            },
            error: function (e) {
                console.log('error e', e);
            },
            remove: function (e) {
                console.log('remove e', e);
            },
            progress: function (e) {
                console.log('progress e', e);
            },
            upload: function (e) {
                console.log('upload e', e);
            },
            cancel: function (e) {
                console.log('cancel e', e);
            },
            complete: function (e) {
                console.log('complete e', e);
            },
            removeHandler: function (e) {
                console.log('removeHandler e', e);
            },
            uploadHandler: function (e) {
                console.log('uploadHandler e', e);
            }
        };

        let uploadOptions = { ...defaultOptions, ...options };

        $target.kendoUpload(uploadOptions);
    }
}