from __future__ import with_statement

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from .SpecialMixerComponent import SpecialMixerComponent
from .SpecialTransportComponent import SpecialTransportComponent
from .SpecialSessionComponent import SpecialSessionComponent
from .SpecialZoomingComponent import SpecialZoomingComponent
from .SpecialViewControllerComponent import DetailViewControllerComponent
from .MIDI_Map import *


# MIDI_NOTE_TYPE = 0
# MIDI_CC_TYPE = 1
# MIDI_PB_TYPE = 2


class YourControllerName(ControlSurface):   # Make sure you update the name
    __doc__ = " Script for YourControllerName in APC emulation mode "   # Make sure you update the name

    _active_instances = []

    def _combine_active_instances():
        track_offset = 0
        scene_offset = 0
        for instance in YourControllerName._active_instances:   # Make sure you update the name
            instance._activate_combination_mode(track_offset, scene_offset)
            track_offset += instance._session.width()
    _combine_active_instances = staticmethod(_combine_active_instances)

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        # self.set_suppress_rebuild_requests(True)
        with self.component_guard():
            self._button_map = []
            self._clip_map = []
            self._slider_map = []
            self._load_MIDI_map()
            self._session = None
            self._session_zoom = None
            self._mixer = None
            self._setup_session_control()
            self._setup_mixer_control()
            self._session.set_mixer(self._mixer)
            self._setup_device_and_transport_control()
            self.set_highlighting_session_component(self._session)
            # self.set_suppress_rebuild_requests(False)
        self._pads = []
        self._load_pad_translations()
        self._do_combine()

    def disconnect(self):
        self._button_map = None
        self._clip_map = None
        self._slider_map = None
        self._pads = None
        self._do_uncombine()
        self._shift_button = None
        self._session = None
        self._session_zoom = None
        self._mixer = None
        ControlSurface.disconnect(self)

    def _do_combine(self):
        if self not in YourControllerName._active_instances:    # Make sure you update the name
            YourControllerName._active_instances.append(self)   # Make sure you update the name
            YourControllerName._combine_active_instances()  # Make sure you update the name

    def _do_uncombine(self):
        if (self in YourControllerName._active_instances) and YourControllerName._active_instances.remove(self):    # Make sure you update the name
            self._session.unlink()
            YourControllerName._combine_active_instances()  # Make sure you update the name

    def _activate_combination_mode(self, track_offset, scene_offset):
        if TRACK_OFFSET != -1:
            track_offset = TRACK_OFFSET
        if SCENE_OFFSET != -1:
            scene_offset = SCENE_OFFSET
        self._session.link_with_track_offset(track_offset, scene_offset)

    def _setup_session_control(self):
        is_momentary = True
        self._session = SpecialSessionComponent(TSB_X, TSB_Y)   # Track selection box size (X,Y) (horizontal, vertical).
        self._session.name = 'Session_Control'
        self._session.set_track_bank_buttons(self._button_map[SESSIONRIGHT], self._button_map[SESSIONLEFT])
        self._session.set_scene_bank_buttons(self._button_map[SESSIONDOWN], self._button_map[SESSIONUP])
        self._session.set_select_buttons(self._button_map[SCENEDN], self._button_map[SCENEUP])
        # range(tsb_x) is the horizontal count for the track selection box
        self._scene_launch_buttons = [self._button_map[SCENELAUNCH[index]] for index in range(TSB_X)]
        # range(tsb_y) Range value is the track selection
        self._track_stop_buttons = [self._button_map[TRACKSTOP[index]] for index in range(TSB_Y)]
        self._session.set_stop_all_clips_button(self._button_map[STOPALLCLIPS])
        self._session.set_stop_track_clip_buttons(tuple(self._track_stop_buttons))
        self._session.selected_scene().name = 'Selected_Scene'
        self._session.selected_scene().set_launch_button(self._button_map[SELSCENELAUNCH])
        self._session.set_slot_launch_button(self._button_map[SELCLIPLAUNCH])
        for scene_index in range(TSB_Y):    # Change range() value to set the vertical count for track selection box
            scene = self._session.scene(scene_index)
            scene.name = 'Scene_' + str(scene_index)
            button_row = []
            scene.set_launch_button(self._scene_launch_buttons[scene_index])
            scene.set_triggered_value(2)
            for track_index in range(TSB_X):    # Change range() value to set the horizontal count for track selection box
                button = self._clip_map[CLIPNOTEMAP[scene_index][track_index]]
                button_row.append(button)
                clip_slot = scene.clip_slot(track_index)
                clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
                clip_slot.set_launch_button(button)
        self._session_zoom = SpecialZoomingComponent(self._session)
        self._session_zoom.name = 'Session_Overview'
        self._session_zoom.set_nav_buttons(self._button_map[ZOOMUP], self._button_map[ZOOMDOWN], self._button_map[ZOOMLEFT], self._button_map[ZOOMRIGHT])

    def _setup_mixer_control(self):

        is_momentary = True
        self._mixer = SpecialMixerComponent(8)
        self._mixer.name = 'Mixer'
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer.master_strip().set_select_button(self._button_map[MASTERSEL])
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        self._mixer.set_select_buttons(self._button_map[TRACKRIGHT], self._button_map[TRACKLEFT])
        self._mixer.set_crossfader_control(self._slider_map[CROSSFADER])
        self._mixer.set_prehear_volume_control(self._slider_map[CUELEVEL])
        self._mixer.master_strip().set_volume_control(self._slider_map[MASTERVOLUME])
        self._mixer.selected_strip().set_arm_button(self._button_map[SELTRACKREC])
        self._mixer.selected_strip().set_solo_button(self._button_map[SELTRACKSOLO])
        self._mixer.selected_strip().set_mute_button(self._button_map[SELTRACKMUTE])
        for track in range(8):
            # My guess is that altering the range here will allow you to alter the range of mixer tracks
            # So if you had a 16 fader mixer, this would come in handy.
            strip = self._mixer.channel_strip(track)
            strip.name = 'Channel_Strip_' + str(track)
            strip.set_arm_button(self._button_map[TRACKREC[track]])
            strip.set_solo_button(self._button_map[TRACKSOLO[track]])
            strip.set_mute_button(self._button_map[TRACKMUTE[track]])
            strip.set_select_button(self._button_map[TRACKSEL[track]])
            strip.set_volume_control(self._slider_map[TRACKVOL[track]])
            strip.set_pan_control(self._slider_map[TRACKPAN[track]])
            strip.set_send_controls((self._slider_map[TRACKSENDA[track]], self._slider_map[TRACKSENDB[track]], self._slider_map[TRACKSENDC[track]]))
            strip.set_invert_mute_feedback(True)

    def _setup_device_and_transport_control(self):
        is_momentary = True
        self._device = DeviceComponent()
        self._device.name = 'Device_Component'
        device_bank_buttons = []
        device_param_controls = []
        for index in range(8):
            device_param_controls.append(self._slider_map[PARAMCONTROL[index]])
            device_bank_buttons.append(self._button_map[DEVICEBANK[index]])
        if None not in device_bank_buttons:
            self._device.set_bank_buttons(tuple(device_bank_buttons))
        if None not in device_param_controls:
            self._device.set_parameter_controls(tuple(device_param_controls))
        self._device.set_on_off_button(self._button_map[DEVICEONOFF])
        self._device.set_bank_nav_buttons(self._button_map[DEVICEBANKNAVLEFT], self._button_map[DEVICEBANKNAVRIGHT])
        self._device.set_lock_button(self._button_map[DEVICELOCK])
        self.set_device_component(self._device)

        detail_view_toggler = DetailViewControllerComponent()
        detail_view_toggler.name = 'Detail_View_Control'
        detail_view_toggler.set_device_clip_toggle_button(self._button_map[CLIPTRACKVIEW])
        detail_view_toggler.set_detail_toggle_button(self._button_map[DETAILVIEW])
        detail_view_toggler.set_device_nav_buttons(self._button_map[DEVICENAVLEFT], self._button_map[DEVICENAVRIGHT])

        transport = SpecialTransportComponent()
        transport.name = 'Transport'
        transport.set_play_button(self._button_map[PLAY])
        transport.set_stop_button(self._button_map[STOP])
        transport.set_record_button(self._button_map[REC])
        transport.set_nudge_buttons(self._button_map[NUDGEUP], self._button_map[NUDGEDOWN])
        transport.set_undo_button(self._button_map[UNDO])
        transport.set_redo_button(self._button_map[REDO])
        transport.set_tap_tempo_button(self._button_map[TAPTEMPO])
        transport.set_quant_toggle_button(self._button_map[RECQUANT])
        transport.set_overdub_button(self._button_map[OVERDUB])
        transport.set_metronome_button(self._button_map[METRONOME])
        transport.set_tempo_control(self._slider_map[TEMPOCONTROL])
        transport.set_loop_button(self._button_map[LOOP])
        transport.set_seek_buttons(self._button_map[SEEKFWD], self._button_map[SEEKRWD])
        transport.set_punch_buttons(self._button_map[PUNCHIN], self._button_map[PUNCHOUT])
        # transport.set_song_position_control(self._ctrl_map[SONGPOSITION]) #still not implemented as of Live 8.1.6

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        track = self.song().view.selected_track
        device_to_select = track.view.selected_device
        if device_to_select is None and len(track.devices) > 0:
            device_to_select = track.devices[0]
        if device_to_select is not None:
            self.song().view.select_device(device_to_select)
        self._device_component.set_device(device_to_select)

    def _load_pad_translations(self):
        if -1 not in DRUM_PADS:
            pad = []
            for row in range(4):
                for col in range(4):
                    pad = (col, row, DRUM_PADS[row*4 + col], PADCHANNEL,)
                    self._pads.append(pad)
            self.set_pad_translations(tuple(self._pads))

    def _load_MIDI_map(self):
        is_momentary = True
        # Buttons / Pads
        for note in range(128):
            button = ButtonElement(is_momentary, BUTTONMESSAGETYPE, BUTTONCHANNEL, note)
            button.name = 'Note_' + str(note)
            self._button_map.append(button)
        self._button_map.append(None)     # add None to the end of the list, selectable with [-1]
        # Clip launcher
        for note in range(128):
            button = ButtonElement(is_momentary, CLIPMESSAGETYPE, CLIPCHANNEL, note)
            button.name = 'Clip_' + str(note)
            self._clip_map.append(button)
        self._clip_map.append(None)     # add None to the end of the list, selectable with [-1]
        # Sliders
        if BUTTONMESSAGETYPE == MIDI_CC_TYPE and BUTTONCHANNEL == SLIDERCHANNEL:
            for ctrl in range(128):
                self._slider_map.append(None)
        else:
            for ctrl in range(128):
                control = SliderElement(MIDI_CC_TYPE, SLIDERCHANNEL, ctrl)
                control.name = 'Ctrl_' + str(ctrl)
                self._slider_map.append(control)
            self._slider_map.append(None)
