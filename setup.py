from setuptools import setup, find_packages


setup(
    name='zeit.cms',
    version='3.30.0.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi core",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'BeautifulSoup',
        'Pillow',
        'SilverCity',
        'ZODB',
        'bugsnag',
        'celery >= 4.0',
        'celery_longterm_scheduler',
        'decorator',
        'docutils',
        'fanstatic[cssmin,jsmin]',
        'gocept.cache >= 2.1',
        'gocept.fckeditor',
        'gocept.form[formlib]>=0.7.5',
        'gocept.jslint>=0.2',
        'gocept.lxml>=0.2.1',
        'gocept.pagelet',
        'gocept.runner',
        'gocept.testing>=1.3',
        'gocept.zcapatch',
        'grokcore.component',
        'grokcore.view',
        'guppy',
        'js.jquery',
        'js.jqueryui',
        'js.mochikit',
        'js.select2',
        'js.underscore',
        'js.vanderlee_colorpicker',
        'lovely.remotetask>=0.5',
        'lxml>=2.0.2',
        'martian',
        'mock',
        'persistent',
        'plone.testing',
        'pypandoc',
        'pyramid_dogpile_cache2',
        'pytest',
        'pytz',
        'redis',
        'repoze.vhm',
        'setuptools',
        'sprout',
        'tblib',
        'transaction',
        'webob',
        'werkzeug',
        'z3c.celery >= 1.2.0.dev0',
        'z3c.conditionalviews>=1.0b2.dev-r91510',
        'z3c.etestbrowser',
        'z3c.flashmessage',
        'z3c.menu.simple>=0.5.1',
        'z3c.noop',
        'z3c.traverser',
        'zc.datetimewidget',
        'zc.form',
        'zc.iso8601',
        'zc.recipe.egg>=1.1.0dev-r84019',
        'zc.relation',
        'zc.set',
        'zc.sourcefactory',
        'zc.table',
        'zdaemon',
        'zeit.connector>=2.12.0.dev0',
        'zeit.find',
        'zeit.objectlog>=1.1.0.dev0',
        'zope.app.appsetup',
        'zope.app.component>=3.4.0b3',
        'zope.app.exception',
        'zope.app.form>=3.6.0',
        'zope.app.locking',
        'zope.app.preference',
        'zope.app.securitypolicy',
        'zope.app.server',
        'zope.app.wsgi',
        'zope.authentication',
        'zope.configuration',
        'zope.copypastemove',
        'zope.error',
        'zope.exceptions',
        'zope.file',
        'zope.i18n>3.4.0',
        'zope.location>=3.4.0b2',
        'zope.login',
        'zope.password',
        'zope.pluggableauth',
        'zope.principalannotation',
        'zope.publisher',
        'zope.sendmail',
        'zope.site',
        'zope.testbrowser [zope-functional-testing]',
        'zope.testing>=3.8.0',
        'zope.traversing',
        'zope.xmlpickle',
        'gocept.httpserverlayer>=1.4.0.dev0',
        'gocept.selenium>=2.2.0.dev0',
        'gocept.jslint>=0.2',
    ],
    entry_points={
        'console_scripts': [
            'dump_references = zeit.cms.relation.migrate:dump_references',
            'load_references = zeit.cms.relation.migrate:load_references',
            'zopeshell = zeit.cms.application:zope_shell',
        ],
        'paste.app_factory': [
            'main=zeit.cms.application:APPLICATION',
        ],
        'paste.filter_factory': [
            'bugsnag=zeit.cms.application:bugsnag_filter',
        ],
        'fanstatic.libraries': [
            'zeit_cms=zeit.cms.browser.resources:lib_css',
            'zeit_cms_js=zeit.cms.browser.resources:lib_js',
            'zeit_cms_content=zeit.cms.content.browser.resources:lib',
            'zeit_cms_workingcopy=zeit.cms.workingcopy.browser.resources:lib',
            'zeit_cms_tagging=zeit.cms.tagging.browser.resources:lib',
            'zeit_cms_clipboard=zeit.cms.clipboard.browser.resources:lib',
            'zeit_workflow=zeit.workflow.browser.resources:lib',

            'zc_table=zeit.cms.browser.resources:zc_table',
            'zc_datetimewidget=zeit.cms.browser.resources:zc_datetimewidget',
        ],
    }
)
