from django.contrib import admin
from domain.models.system import MenuFolder, MenuItem
from domain.models.user import UserGroupMenu

@admin.register(MenuFolder)
class MenuFolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'FolderName', 'Parent', '_order', '_status', '_created', '_modified')
    search_fields = ('FolderName',)
    list_filter = ('_status',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('MenuCode', 'MenuName', 'MenuFolder', 'Url', 'Popup', '_order', '_status', '_created', '_modified')
    search_fields = ('MenuName', 'MenuCode')
    list_filter = ('_status',)

@admin.register(UserGroupMenu)
class UserGroupMenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'UserGroup', 'MenuCode', 'AuthCode', '_status', '_created', '_modified')
    search_fields = ('MenuCode', 'AuthCode')
    list_filter = ('UserGroup',)

