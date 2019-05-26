configurationData = configuration_data()
configurationData.set('PACKAGE_NAME', meson.project_name())
configurationData.set('LOCALE_DIR', LOCALE_DIR)
configure_file(input: 'config.h.in', output: 'config.h', configuration: configurationData)

install_data('Applet.plugin', install_dir: LIB_INSTALL_DIR)

AppletSources = [
'Applet.vala',
'widgets/IndicatorButton.vala',
'widgets/CustomMenuButton.vala',
'widgets/Popover.vala',
'widgets/CustomScale.vala',
'helpers/DimHelper.vala',
'helpers/LightHelper.vala',
'helpers/SubprocessHelper.vala',
'helpers/ConfigHelper.vala',
'models/Flame.vala',
'models/Dim.vala',
'models/Light.vala'
]

AppletDependencies = [
dependency('gtk+-3.0', version: '>=3.18'), 
dependency('budgie-1.0', version: '>=2')
]

AppletValaArgs = [
'--pkg=config', 
'--vapidir=' + VAPI_DIR, 
'--target-glib=2.38', 
'--enable-deprecated'
]

AppletCArgs = [
'-include', 
'config.h'
]

shared_library('advancedbrightnesscontroller', 
AppletSources, 
dependencies: AppletDependencies, 
vala_args: AppletValaArgs, 
c_args: AppletCArgs, 
install: true, 
install_dir: LIB_INSTALL_DIR)