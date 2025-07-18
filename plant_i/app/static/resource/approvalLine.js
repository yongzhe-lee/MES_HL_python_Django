// ApprovalLine 공통 등록 (중복 실행 방지)
if (!window.__WO_APPROVAL_LINE_SCRIPT_LOADED__) {
    window.__WO_APPROVAL_LINE_SCRIPT_LOADED__ = true;

    if (typeof window.ApprovalLine === 'undefined') {
        window.ApprovalLine = class ApprovalLine {
            constructor(woType, rqstDprYn, rqstInspYn) {
                this.baseUrl = '/api/kmms/work_order';
                this.woType = woType;
                this.rqstDprYn = rqstDprYn;
                this.rqstInspYn = rqstInspYn;
                this.currentStatus = 'WOS_RQ'; // 기본값: 작업요청
                this.dataPk = '';
                this.woStatusData = [
                    {codePk: '', codeCd: '', codeNm: '전체'},
                    {codePk: 0, codeCd: 'WOS_RW', codeNm: '요청작성중'},
                    {codePk: 1, codeCd: 'WOS_RQ', codeNm: '작업요청'},
                    {codePk: 2, codeCd: 'WOS_OC', codeNm: '요청승인'},
                    {codePk: 3, codeCd: 'WOS_RB', codeNm: '요청반려'},
                    {codePk: 4, codeCd: 'WOS_AP', codeNm: '작업승인'},
                    {codePk: 5, codeCd: 'WOS_RJ', codeNm: '작업요청반려'},
                    {codePk: 7, codeCd: 'WOS_CM', codeNm: '작업완료'},
                    {codePk: 8, codeCd: 'WOS_CL', codeNm: '완료'},
                ];
                this.init();
            }
            init() {
                const initializeMenu = () => {
                    this.setupWoTypeDisplay();
                    if (this.dataPk && this.dataPk !== 'None' && this.dataPk !== '') {
                        this.show(this.dataPk);
                    }
                };
                document.addEventListener('DOMContentLoaded', initializeMenu, { passive: true });
                requestAnimationFrame(() => {
                    initializeMenu();
                });
            }
            getWoTypeNm() {
                if (this.woType === 'WO' && this.rqstDprYn === 'Y') {
                    return '작업일보';
                } else if (this.woType === 'WO' && this.rqstInspYn === 'Y') {
                    return '점검';
                } else if (this.woType === 'PM') {
                    return 'CM';
                } else {
                    return '작업';
                }
            }
            setupWoTypeDisplay(modalType = '') {
                const woTypeNm = this.getWoTypeNm();
                
                // 모달 타입에 따라 다른 ID 사용
                let woTypeDisplayId = 'woTypeDisplay';
                if (modalType === 'MyWorkReq') {
                    woTypeDisplayId = 'woTypeDisplay_MyWorkReq';
                } else if (modalType === 'MyWorkAppr') {
                    woTypeDisplayId = 'woTypeDisplay_MyWorkAppr';
                }
                
                const woTypeDisplay = document.getElementById(woTypeDisplayId);
                if (woTypeDisplay) {
                    woTypeDisplay.textContent = woTypeNm;
                }
            }
            renderFilteredStatusMenu(apprLineArray, modalType = '') {			
                console.log(`Approval Line: ${apprLineArray}`);
                
                // 모달 타입에 따라 다른 ID 사용
                let statusMenuItemsId = 'statusMenuItems';
                let woTypeDisplayId = 'woTypeDisplay';
                
                if (modalType === 'MyWorkReq') {
                    statusMenuItemsId = 'statusMenuItems_MyWorkReq';
                    woTypeDisplayId = 'woTypeDisplay_MyWorkReq';
                } else if (modalType === 'MyWorkAppr') {
                    statusMenuItemsId = 'statusMenuItems_MyWorkAppr';
                    woTypeDisplayId = 'woTypeDisplay_MyWorkAppr';
                }
                
                const container = document.getElementById(statusMenuItemsId);        
                if (!container) return;
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }
                const filteredStatusData = this.woStatusData.filter(status => {
                    if (!status.codeCd) return false;
                    const statusCode = status.codeCd.split('_').pop();
                    return apprLineArray.includes(statusCode);
                });
                filteredStatusData.forEach((status, index) => {
                    const menuItem = document.createElement('span');
                    menuItem.className = 'approval-item';
                    menuItem.textContent = status.codeNm;
                    menuItem.dataset.statusCode = status.codeCd;
                    const statusCode = status.codeCd.split('_').pop();
                    // currentStatus가 승인라인 배열 안에 있을 때만 활성화
                    if (this.currentStatus === statusCode && apprLineArray.includes(statusCode)) {
                        menuItem.classList.add('active');
                    }
                    container.appendChild(menuItem);
                    // 구분자 추가
                    if (index < filteredStatusData.length - 1) {
                        const separator = document.createElement('span');
                        separator.className = 'approval-separator';
                        separator.textContent = '>';
                        container.appendChild(separator);
                    }
                });
            }
            show(dataPk, modalType = '') {
                // 현재 상태 조회를 먼저 수행
                const paramCurrentStatus = {
                    action: 'findOneWo',
                    workOrderPk: dataPk,
                };
                const workOrderInfo = AjaxUtil.getSyncData(this.baseUrl, paramCurrentStatus);
                if (workOrderInfo && workOrderInfo.wo_status_cd) {
                    this.currentStatus = workOrderInfo.wo_status_cd.substring(workOrderInfo.wo_status_cd.lastIndexOf('_') + 1);
                }
				console.log(`Current Status: ${this.currentStatus}`);
                // 승인 라인 조회
                const paramApprLine = {
                    action: 'getFullApprLine',
                    workOrderPk: dataPk,
                };
                const appr_line = AjaxUtil.getSyncData(this.baseUrl, paramApprLine);
                // 현재 상태가 설정된 후에만 메뉴 렌더링
                if (appr_line && appr_line.full_appr_line) {
                    const apprLineArray = appr_line.full_appr_line.split(',');
                    this.renderFilteredStatusMenu(apprLineArray, modalType);					
                }
            }
            onWorkOrderClick(workOrderPk, modalType = '') {
				console.log(`Work Order clicked: ${workOrderPk}, Modal Type: ${modalType}`);
                this.dataPk = workOrderPk;
                
                // 모달 타입에 따라 다른 ID 사용
                let approvalLineId = 'woApprovalLine';
                let dataPkId = 'dataPk';
                let woTypeDisplayId = 'woTypeDisplay';
                let statusMenuItemsId = 'statusMenuItems';
                
                if (modalType === 'MyWorkReq') {
                    approvalLineId = 'woApprovalLine_MyWorkReq';
                    dataPkId = 'dataPk_MyWorkReq';
                    woTypeDisplayId = 'woTypeDisplay_MyWorkReq';
                    statusMenuItemsId = 'statusMenuItems_MyWorkReq';
                } else if (modalType === 'MyWorkAppr') {
                    approvalLineId = 'woApprovalLine_MyWorkAppr';
                    dataPkId = 'dataPk_MyWorkAppr';
                    woTypeDisplayId = 'woTypeDisplay_MyWorkAppr';
                    statusMenuItemsId = 'statusMenuItems_MyWorkAppr';
                }
                
                if (this.dataPk && this.dataPk !== 'None' && this.dataPk !== '') {
                    $(`#${approvalLineId}`).css("display", "block");
                    this.show(this.dataPk, modalType);
                } else {
                    $(`#${approvalLineId}`).css("display", "none");
                }
            }
        };
    }
    if (typeof window.approvalLine === 'undefined') {
        const approvalLine = new window.ApprovalLine('WO', 'N', 'N');
        window.approvalLine = approvalLine;
    }
} 