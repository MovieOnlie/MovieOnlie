import xadmin
from .models import Category, Page
from xadmin import views


#自定义主题
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

xadmin.site.register(views.BaseAdminView,BaseSetting)


#自定义页眉页脚
class GlobalSetting(object):
    #页眉
    site_title = "China NO.1"
    #页脚
    site_footer = "NBteam的后台管理"
    #多表缩进
    menu_style = "accordion"

    # 设置app模块的标题
    apps_label_title = {
        'Movieapp': '影片管理'
    }

    # 设置app模块的图标
    apps_icons = {
        'Movieapp': 'glyphicon glyphicon-film'
    }

    # 设置模型在后台显示的图标
    global_models_icon = {
        Category: 'glyphicon glyphicon-link',
        Page: 'glyphicon glyphicon-sound-dolby'
    }


xadmin.site.register(views.CommAdminView,GlobalSetting)

class CategoryAdmin(object):
    # 显示的列
    list_display = ['name', 'content', 'likes']
    # 搜索的字段
    search_fields = ['name', 'content']

class PageAdmin(object):
    list_display = ['name', 'url', 'views','category']
    search_fields = ['name']

xadmin.site.register(Category,CategoryAdmin)
xadmin.site.register(Page,PageAdmin)
