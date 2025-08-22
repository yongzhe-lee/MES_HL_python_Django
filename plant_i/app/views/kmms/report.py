from django import db
from domain.services.kmms.report import CmReportService
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

def report(context):
    '''
    api/kmms/report    통계정보
    '''
    items = []
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    action = gparam.get('action', 'read')

    reportService = CmReportService()

    try:
        # 설비별 월간 고장현황
        if action == 'facility_monthly_status':            
            searchYear = gparam.get('searchYear', None)
            deptTree = gparam.get('deptTree', None)
            equipLocTree = gparam.get('equipLocTree', None)

            items = reportService.facility_monthly_status(searchYear, deptTree, equipLocTree)

        # 설비별 월간 정비비용
        elif action == 'monthly_maintenance_cost':
            searchYear = gparam.get('searchYear', None)
            woType = gparam.get('woType', None)
            maintTypeCd = gparam.get('maintTypeCd', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.monthly_maintenance_cost(searchYear, woType, maintTypeCd, deptPk)

        # 기간별 불용처리 설비 현황
        elif action == 'facility_treatment_status':
            startYear = gparam.get('searchYear_start', None)
            endYear = gparam.get('searchYear_end', None)

            items = reportService.facility_treatment_status(startYear, endYear)

        # 기간별 불용처리 설비 현황 상세
        elif action == 'facility_treatment_status_detail':
            yearMon = gparam.get('yearMon', None)
            
            items = reportService.facility_treatment_status_detail(yearMon)

        # 설비별 MTTR/MTBF
        elif action == 'facility_mttr_mtbf':
            searchText = gparam.get('searchText', None)
            deptPk = gparam.get('deptPk', None)
            startDt = gparam.get('start_dt', None)
            endDt = gparam.get('end_dt', None)

            items = reportService.facility_mttr_mtbf(searchText, deptPk, startDt, endDt)

        # 카테고리별 설비 현황
        elif action == 'category_equipment_status':            
            locPk = gparam.get('plantLoc', None)

            items = reportService.category_equipment_status(locPk)

        # 중요도별 설비 고장 현황
        elif action == 'critical_equipment_status':
            
            items = reportService.critical_equipment_status()

        # 중요도별 설비 고장 현황 상세
        elif action == 'critical_equipment_status_detail':
            importRankPk = gparam.get('importRankPk', None)

            items = reportService.critical_equipment_status_detail(importRankPk)

        # 설비별 정비비용
        elif action == 'facility_maintenance_cost':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            searchText = gparam.get('searchText', None)
            deptPk = gparam.get('deptPk', None)
            locPk = gparam.get('locPk', None)

            items = reportService.facility_maintenance_cost(dateType, startDt, endDt, searchText, deptPk, locPk)

        # 설비별 고장시간
        elif action == 'facility_downtime':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            searchText = gparam.get('searchText', None)
            deptPk = gparam.get('deptPk', None)
            locPk = gparam.get('locPk', None)

            items = reportService.facility_downtime(dateType, startDt, endDt, searchText, deptPk, locPk)

        # 설비별 사양 목록
        elif action == 'facility_specifications':
            searchText = gparam.get('searchText', None)
            deptPk = gparam.get('deptPk', None)
            locPk = gparam.get('locPk', None)

            items = reportService.facility_specifications(searchText, deptPk, locPk)

############# 작업통계 ################################################################

        # 부서별 기간별 WO 발행 실적
        elif action == 'wm_wo_dept_performance':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.wm_wo_dept_performance(dateType, startDt, endDt, deptPk)

        # 부서별 기간별 작업비용
        elif action == 'dept_work_costs':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.dept_work_costs(dateType, startDt, endDt, deptPk)

        # 상위 작업시간 WO
        elif action == 'top_working_hours_wo':
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            reqDeptPk = gparam.get('reqDeptPk', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.top_working_hours_wo(startDt, endDt, reqDeptPk, deptPk)

        # 정비비용 현황
        elif action == 'conservation_cost_status':
            searchYearMonth = gparam.get('searchYearMonth', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.conservation_cost_status(searchYearMonth, deptPk)

        # 작업비용 상위 WO
        elif action == 'top_work_cost_wo':
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            reqDeptPk = gparam.get('reqDeptPk', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.top_work_cost_wo(startDt, endDt, reqDeptPk, deptPk)

        # 아웃소싱 작업건수
        elif action == 'outsourced_tasks_count':
            dateType = gparam.get('dateType', None)
            searchYearMonth = gparam.get('searchYearMonth', None)
            searchYear = gparam.get('searchYear', None)
            workSrc = gparam.get('workSrc', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.outsourced_tasks_count(dateType, searchYearMonth, searchYear, workSrc, deptPk)

        # 아웃소싱 작업건수 차트
        elif action == 'outsourced_tasks_count_total':
            dateType = gparam.get('dateType', None)
            searchYearMonth = gparam.get('searchYearMonth', None)
            searchYear = gparam.get('searchYear', None)
            workSrc = gparam.get('workSrc', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.outsourced_tasks_count_total(dateType, searchYearMonth, searchYear, workSrc, deptPk)

        # 부서별 예방 정비율
        elif action == 'dept_pm_rate':
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.dept_pm_rate(startDt, endDt, deptPk)

        # 팀별 고장비용 현황
        elif action == 'team_breakdown_costs':
            searchYear = gparam.get('searchYear', None)
            maintTypeCd = gparam.get('maintTypeCd', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.team_breakdown_costs(searchYear, maintTypeCd, deptPk)

        # 부서별 기간별 지연작업 목록
        elif action == 'dept_overdue_tasks':
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            deptPk = gparam.get('deptPk', None)
            reqDeptPk = gparam.get('reqDeptPk', None)

            items = reportService.dept_overdue_tasks(startDt, endDt, deptPk, reqDeptPk)

        # 부서별 기간별 작업 준수율
        elif action == 'dept_task_compliance_rate':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)

            rows = reportService.dept_task_compliance_rate(dateType, startDt, endDt)
            footer = reportService.dept_task_compliance_rate_footer(dateType, startDt, endDt)
            items = {"rows": rows, "footer": footer}

        # 부서별 작업 요청 통계
        elif action == 'dept_work_request_stats':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)
            reqDeptPk = gparam.get('reqDeptPk', None)
            deptPk = gparam.get('deptPk', None)

            items = reportService.dept_work_request_stats(dateType, startDt, endDt, reqDeptPk, deptPk)

############# PM통계 ################################################################

        # 카테고리별 PM 현황
        elif action == 'pm_status_by_category':

            items = reportService.pm_status_by_category()

        # 부서별 PM WO 완료율
        elif action == 'pm_wo_completion_rate':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)

            rows = reportService.pm_wo_completion_rate(dateType, startDt, endDt)
            footer = reportService.pm_wo_completion_rate_footer(dateType, startDt, endDt)
            items = {"rows": rows, "footer": footer}

############# 점검통계 ################################################################

        # 설비종류별 점검마스터
        elif action == 'facility_inspection_master':
            
            items = reportService.facility_inspection_master()

        # 점검결과 이상 설비목록
        elif action == 'inspection_issues':
            searchText = gparam.get('searchText', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)

            items = reportService.inspection_issues(searchText, startDt, endDt)

        # 점검 수행 통계
        elif action == 'inspection_stats':
            dateType = gparam.get('dateType', None)
            startDt = gparam.get('startDt', None)
            endDt = gparam.get('endDt', None)

            items = reportService.inspection_stats(dateType, startDt, endDt)

    except Exception as ex:
        source = 'kmms/report : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)        

    return items
