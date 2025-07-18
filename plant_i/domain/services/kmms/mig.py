from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class MigService():
	def __init__(self):
		return

	def delete_dept(self, site):	
		dic_param = {'site': site}
		sql = ''' 
			/* delete [mig-dept-mapper.xml] */
			DELETE FROM cm_mig_dept
			;
			'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_dept', ex)
			raise ex

	def migrate_dept(self, site):
		items = []
		dic_param = {'site': site}

		sql = ''' 
			/* execute [mig-dept-mapper.xml] */
			CALL cm_prc_mig_dept()
			;
			'''

		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_dept', ex)
			raise ex

		return items

	def delete_user_info(self, site):	
		dic_param = {'site': site}
		sql = ''' 
			/* delete [mig-dept-mapper.xml] */
			DELETE FROM cm_mig_user
			;
			'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_user_info', ex)
			raise ex

	def migrate_user_info(self, site):
		items = []
		dic_param = {'site': site}

		sql = ''' 
			/* execute [mig-user-info-mapper.xml] */
			CALL cm_prc_mig_user()
			;
			'''

		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_user_info', ex)
			raise ex

		return items

	def delete_location(self, site):
		dic_param = {'site': site}
		sql = ''' 
			DELETE FROM cm_mig_loc
			;
			'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_location', ex)
			raise ex

	def migrate_location(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			CALL cm_prc_mig_loc()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_location', ex)
			raise ex
		return items

	def delete_supplier(self, site):
		dic_param = {'site': site}
		sql = ''' 
			DELETE FROM cm_mig_supplier
			;
			'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_supplier', ex)
			raise ex

	def migrate_supplier(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			CALL cm_prc_mig_supplier()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_supplier', ex)
			raise ex
		return items

	def delete_base_code(self, site):
		dic_param = {'site': site}
		sql = ''' 
			DELETE FROM cm_mig_base_code
			;
			'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_base_code', ex)
			raise ex

	def migrate_base_code(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			CALL cm_prc_mig_base_code()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_base_code', ex)
			raise ex
		return items

	def delete_material(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_mtrl
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_material', ex)
			raise ex

	def migrate_material(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-material-mapper.xml] */
			CALL cm_prc_mig_mtrl()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_material', ex)
			raise ex
		return items

	def delete_equip_class(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_class
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equip_class', ex)
			raise ex

	def migrate_equip_class(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equip-class-mapper.xml] */
			CALL cm_prc_mig_equip_class()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equip_class', ex)
			raise ex
		return items

	def delete_equip_type(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_type
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equip_type', ex)
			raise ex

	def migrate_equip_type(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equip-type-mapper.xml] */
			CALL cm_prc_mig_equip_type()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equip_type', ex)
			raise ex
		return items

	def delete_equipment(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equipment', ex)
			raise ex

	def migrate_equipment(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equipment-mapper.xml] */
			CALL cm_prc_mig_equip()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equipment', ex)
			raise ex
		return items

	def delete_equip_part_mtrl(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_part_mtrl
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equip_part_mtrl', ex)
			raise ex

	def migrate_equip_part_mtrl(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equip-part-mtrl-mapper.xml] */
			CALL cm_prc_mig_equip_part_mtrl()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equip_part_mtrl', ex)
			raise ex
		return items

	def delete_equip_spec(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_spec
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equip_spec', ex)
			raise ex

	def migrate_equip_spec(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equip-spec-mapper.xml] */
			CALL cm_prc_mig_equip_spec()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equip_spec', ex)
			raise ex
		return items

	def delete_pm(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_pm
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_pm', ex)
			raise ex

	def migrate_pm(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-pm-mapper.xml] */
			CALL cm_prc_mig_pm()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_pm', ex)
			raise ex
		return items

	def delete_equipchkmast(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_chk_mst
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equipchkmast', ex)
			raise ex

	def migrate_equipchkmast(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equipchkmast-mapper.xml] */
			CALL cm_prc_mig_equip_chk_mst()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equipchkmast', ex)
			raise ex
		return items

	def delete_chkequip(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_chk_equip
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_chkequip', ex)
			raise ex

	def migrate_chkequip(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-chkequip-mapper.xml] */
			CALL cm_prc_mig_chk_equip()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_chkequip', ex)
			raise ex
		return items

	def delete_equipchkitem(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_chk_mst_item
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equipchkitem', ex)
			raise ex

	def migrate_equipchkitem(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equipchkitem-mapper.xml] */
			CALL cm_prc_mig_equip_chk_mst_item()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equipchkitem', ex)
			raise ex
		return items

	def delete_stor_loc_addr(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_stor_loc_addr
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_stor_loc_addr', ex)
			raise ex

	def migrate_stor_loc_addr(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-stor-loc-addr-mapper.xml] */
			CALL cm_prc_mig_stor_loc_addr()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_stor_loc_addr', ex)
			raise ex
		return items

	def delete_mtrlinout(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_mtrlinout
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_mtrlinout', ex)
			raise ex

	def migrate_mtrlinout(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-mtrlinout-mapper.xml] */
			CALL cm_prc_mig_mtrlinout()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_mtrlinout', ex)
			raise ex
		return items

	def delete_wo(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_wo
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_wo', ex)
			raise ex

	def migrate_wo(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-wo-mapper.xml] */
			CALL cm_prc_mig_wo()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_wo', ex)
			raise ex
		return items

	def delete_wo_fault_loc(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_wo_fault_loc
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_wo_fault_loc', ex)
			raise ex

	def migrate_wo_fault_loc(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-wo-fault-loc-mapper.xml] */
			CALL cm_prc_mig_wo_fault_loc()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_wo_fault_loc', ex)
			raise ex
		return items

	def delete_mtrl_photo(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_mtrl_photo
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_mtrl_photo', ex)
			raise ex

	def migrate_mtrl_photo(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-mtrl-photo-mapper.xml] */
			CALL cm_prc_mig_mtrl_photo()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_mtrl_photo', ex)
			raise ex
		return items

	def delete_equip_photo(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_photo
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equip_photo', ex)
			raise ex

	def migrate_equip_photo(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equip-photo-mapper.xml] */
			CALL cm_prc_mig_equip_photo()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equip_photo', ex)
			raise ex
		return items

	def delete_equip_file(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_equip_file
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_equip_file', ex)
			raise ex

	def migrate_equip_file(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-equip-file-mapper.xml] */
			CALL cm_prc_mig_equip_file()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_equip_file', ex)
			raise ex
		return items

	def delete_tech_file(self, site):
		dic_param = {'site': site}
		sql = '''
			DELETE FROM cm_mig_tech_file
			;
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.delete_tech_file', ex)
			raise ex

	def migrate_tech_file(self, site):
		items = []
		dic_param = {'site': site}
		sql = ''' 
			/* execute [mig-tech-file-mapper.xml] */
			CALL cm_prc_mig_tech_file()
			;
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate_tech_file', ex)
			raise ex
		return items

	def migrate(self, site):
		items = []
		dic_param = {'site': site}

		sql = ''' 
			/* default migration */
			SELECT 'Default migration completed' as result
			;
			'''

		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'MigService.migrate', ex)
			raise ex

		return items
