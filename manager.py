# _*_ coding:utf-8 _*_
"""程序入口"""
from flask import session

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from flask_session import Session
from iHome import get_app,db


"""选择不同模式得到的flask对象app"""
app = get_app('dev')

"""创建脚本管理器"""
manager = Manager(app)

"""让迁移时，app和db关联"""
Migrate(app,db)

"""将数据库迁移的脚本，命令添加到脚本管理器对象"""
manager.add_command('db',MigrateCommand)



if __name__ == '__main__':
    """查看路由映射的函数"""
    print app.url_map

    """在manager启动那个开关编辑runserver，才可以点击运行"""
    manager.run()