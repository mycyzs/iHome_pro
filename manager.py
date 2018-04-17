# _*_ coding:utf-8 _*_
"""程序入口"""
from flask import session

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from flask_session import Session
from iHome import app,db




"""创建脚本管理器"""
manager = Manager(app)

"""让迁移时，app和db关联"""
Migrate(app,db)

"""将数据库迁移的脚本，命令添加到脚本管理器对象"""
manager.add_command('db',MigrateCommand)

"""将session数据写入redis数据库"""
Session(app)



@app.route('/')
def index():
    """测试redis是否链接"""
    # redis_strict.set('name','python')
    """测试session过期时间"""
    # session['celery'] = 1000
    return 'index'

if __name__ == '__main__':
    """在manager启动那个开关编辑runserver，才可以点击运行"""
    manager.run()