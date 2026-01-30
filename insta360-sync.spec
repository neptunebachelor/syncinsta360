# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config.ini', '.'), ('insta360_api', 'insta360_api')],
    hiddenimports=['requests', 'urllib3', 'chardet', 'certifi', 'idna', 'insta360_api.pb2.active_sensor_device_pb2', 'insta360_api.pb2.authorization_operation_type_pb2', 'insta360_api.pb2.authorization_result_pb2', 'insta360_api.pb2.battery_low_pb2', 'insta360_api.pb2.battery_pb2', 'insta360_api.pb2.battery_update_pb2', 'insta360_api.pb2.bluetooth_pb2', 'insta360_api.pb2.bt_central_notification_pb2', 'insta360_api.pb2.bt_central_pb2', 'insta360_api.pb2.button_press_params_pb2', 'insta360_api.pb2.button_press_pb2', 'insta360_api.pb2.calibrate_gyro_pb2', 'insta360_api.pb2.camera_posture_pb2', 'insta360_api.pb2.camera_wifi_connection_result_pb2', 'insta360_api.pb2.cancel_capture_pb2', 'insta360_api.pb2.cancel_request_authorization_pb2', 'insta360_api.pb2.capture_auto_split_pb2', 'insta360_api.pb2.capture_state_pb2', 'insta360_api.pb2.capture_stopped_pb2', 'insta360_api.pb2.chargebox_pb2', 'insta360_api.pb2.charging_command_type_pb2', 'insta360_api.pb2.check_authorization_pb2', 'insta360_api.pb2.close_camera_oled_pb2', 'insta360_api.pb2.current_capture_status_pb2', 'insta360_api.pb2.delete_files_pb2', 'insta360_api.pb2.detect_face_pb2', 'insta360_api.pb2.error_pb2', 'insta360_api.pb2.exposure_pb2', 'insta360_api.pb2.exposure_update_pb2', 'insta360_api.pb2.extra_info_pb2', 'insta360_api.pb2.fileinfo_list_pb2', 'insta360_api.pb2.file_type_pb2', 'insta360_api.pb2.flicker_pb2', 'insta360_api.pb2.fw_upgrade_state_pb2', 'insta360_api.pb2.get_button_press_params_pb2', 'insta360_api.pb2.get_current_button_status_pb2', 'insta360_api.pb2.get_current_capture_status_pb2', 'insta360_api.pb2.get_file_extra_pb2', 'insta360_api.pb2.get_file_finish_pb2', 'insta360_api.pb2.get_file_list_pb2', 'insta360_api.pb2.get_file_pb2', 'insta360_api.pb2.get_flowstate_enable_pb2', 'insta360_api.pb2.get_gyro_pb2', 'insta360_api.pb2.get_mini_thumbnail_pb2', 'insta360_api.pb2.get_multi_photography_options_pb2', 'insta360_api.pb2.get_options_pb2', 'insta360_api.pb2.get_photography_options_pb2', 'insta360_api.pb2.get_sfr_result_pb2', 'insta360_api.pb2.get_sfr_status_pb2', 'insta360_api.pb2.get_sync_capture_mode_pb2', 'insta360_api.pb2.get_timelapse_options_pb2', 'insta360_api.pb2.get_whiteblance_status_pb2', 'insta360_api.pb2.get_wifi_connection_info_pb2', 'insta360_api.pb2.key_pressed_pb2', 'insta360_api.pb2.live_stream_params_update_pb2', 'insta360_api.pb2.media_pb2', 'insta360_api.pb2.message_code_pb2', 'insta360_api.pb2.multi_photography_options_pb2', 'insta360_api.pb2.offset_state_pb2', 'insta360_api.pb2.open_camera_oled_pb2', 'insta360_api.pb2.open_iperf_service_pb2', 'insta360_api.pb2.options_pb2', 'insta360_api.pb2.photography_options_pb2', 'insta360_api.pb2.photo_pb2', 'insta360_api.pb2.request_authorization_pb2', 'insta360_api.pb2.sd_card_speed_pb2', 'insta360_api.pb2.sensor_pb2', 'insta360_api.pb2.set_access_camera_file_state_pb2', 'insta360_api.pb2.set_appid_pb2', 'insta360_api.pb2.set_button_press_params_pb2', 'insta360_api.pb2.set_charging_data_pb2', 'insta360_api.pb2.set_file_extra_pb2', 'insta360_api.pb2.set_flowstate_enable_pb2', 'insta360_api.pb2.set_key_time_point_pb2', 'insta360_api.pb2.set_multi_photography_options_pb2', 'insta360_api.pb2.set_options_pb2', 'insta360_api.pb2.set_photography_options_pb2', 'insta360_api.pb2.set_standby_mode_pb2', 'insta360_api.pb2.set_sync_capture_mode_pb2', 'insta360_api.pb2.set_timelapse_options_pb2', 'insta360_api.pb2.set_wifi_connection_info_pb2', 'insta360_api.pb2.set_wifi_seize_pb2', 'insta360_api.pb2.shutdown_pb2', 'insta360_api.pb2.start_bullettime_pb2', 'insta360_api.pb2.start_capture_pb2', 'insta360_api.pb2.start_hdr_pb2', 'insta360_api.pb2.start_live_stream_pb2', 'insta360_api.pb2.start_timelapse_pb2', 'insta360_api.pb2.start_timeshift_pb2', 'insta360_api.pb2.stop_bullettime_pb2', 'insta360_api.pb2.stop_capture_pb2', 'insta360_api.pb2.stop_hdr_pb2', 'insta360_api.pb2.stop_live_stream_pb2', 'insta360_api.pb2.stop_timelapse_pb2', 'insta360_api.pb2.stop_timeshift_pb2', 'insta360_api.pb2.storage_pb2', 'insta360_api.pb2.storage_update_pb2', 'insta360_api.pb2.sync_capture_mode_pb2', 'insta360_api.pb2.sync_capture_mode_update_pb2', 'insta360_api.pb2.take_picture_pb2', 'insta360_api.pb2.take_picture_state_update_pb2', 'insta360_api.pb2.temperature_pb2', 'insta360_api.pb2.timelapse_pb2', 'insta360_api.pb2.timelapse_status_update_pb2', 'insta360_api.pb2.track_pb2', 'insta360_api.pb2.upload_gps_pb2', 'insta360_api.pb2.video_pb2', 'insta360_api.pb2.wifi_connection_info_pb2', 'insta360_api.pb2.window_crop_info_pb2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='insta360-sync',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
