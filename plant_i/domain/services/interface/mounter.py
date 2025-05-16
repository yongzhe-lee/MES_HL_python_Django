
import json
from datetime import datetime
from domain.models.interface import IFMounterPickupRate
from domain.services.logging import LogWriter

from domain.services.date import DateUtil

class IFFujiMounterService(object):
    """
    Interface for Fuji Mounter Service.
    """
    def __init__(self):
        return
    
    def smt_mnt_pickup_rate_topic_handler(self, topic, payload):
        '''
        pickuprate 관련 데이터 저장
        '''
        source  = f"IFEquipmentResultService.smt_mnt_pickup_rate_topic_handler - topic :{topic}"
        print(topic, payload)
        dic_payload = None

        try:
            dic_payload = json.loads(payload)
        except Exception as ppex:
            LogWriter.add_dblog("error", source, ppex)
            return 0


        now = DateUtil.get_current_datetime()
        pickup_rate_items = dic_payload.get("Monitor", [])

        count = 1
        for r in pickup_rate_items:

            job = r.get('job')
            machine = r.get('machine')
            position = r.get('position')
            partNumber = r.get('partNumber')
            fidl = r.get('fidl')
            pickup = r.get('pickup')
            noPickup = r.get('noPickup')
            usage = r.get('usage')
            reject = r.get('reject')
            error = r.get('error')
            dislodge = r.get('dislodge')
            rescan = r.get('rescan')
            lcr = r.get('lcr')
            ratioPickup = r.get('ratioPickup')
            ratioReject = r.get('ratioReject')
            ratioError = r.get('ratioError')
            ratioDislodge = r.get('ratioDislodge')
            ratioSuccess = r.get('ratioSuccess')
            str_start_dt = r.get('start_dt')
            start_dt = datetime.strptime(str_start_dt,'%Y-%m-%dT%H:%M:%S%z')

            if_pickup_rate = IFMounterPickupRate()
            if_pickup_rate.job = job
            if_pickup_rate.machine = machine
            if_pickup_rate.position = position
            if_pickup_rate.partNumber = partNumber
            if_pickup_rate.fidl = fidl
            if_pickup_rate.pickup = pickup
            if_pickup_rate.noPickup = noPickup
            if_pickup_rate.usage = usage
            if_pickup_rate.reject = reject
            if_pickup_rate.error = error
            if_pickup_rate.dislodge = dislodge
            if_pickup_rate.rescan = rescan
            if_pickup_rate.lcr = lcr
            if_pickup_rate.ratioPickup = ratioPickup
            if_pickup_rate.ratioReject = ratioReject
            if_pickup_rate.ratioError = ratioError
            if_pickup_rate.ratioDislodge = ratioDislodge
            if_pickup_rate.ratioSuccess = ratioSuccess
            if_pickup_rate.start_dt = start_dt
            if_pickup_rate._created = now
            
            if_pickup_rate.save()

            count =count+1

        return count