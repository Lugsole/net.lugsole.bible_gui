

conf = configuration_data()
conf.set('version', meson.project_version())
conf.set('version_date', version_date)
conf.set('APPLICATION_ID', application_id)
conf.set('application_path', application_path)
conf.set('file_name_suffix', file_name_suffix)
conf.set('application_name_suffix', application_name_suffix)

desktop_file = i18n.merge_file(
  input: configure_file(
    output: application_id+ '.desktop.in',
    input: 'net.lugsole.bible_gui.desktop.in.in',
    configuration: conf),
  output: application_id+'.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif
appstream_file = configure_file(
  input: 'net.lugsole.bible_gui.appdata.xml.in',
  output: application_id+'.appdata.xml',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'metainfo')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

schema_src = 'net.lugsole.bible_gui.gschema.xml'
schema_src = configure_file(
  input: 'net.lugsole.bible_gui.gschema.xml.in',
  output: application_id+'.gschema.xml',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'glib-2.0/schemas')
)
compiled = gnome.compile_schemas(build_by_default: true,
                                 depend_files: schema_src)

install_data(schema_src,
  rename: application_id+'.gschema.xml',
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'glib-2.0/schemas')
)

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), application_id)
install_data('kjv.tsv',
  install_dir: pkgdatadir
)


subdir('icons')
