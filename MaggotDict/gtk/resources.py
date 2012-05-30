# -*- coding: utf-8 -*-

__all__ = ('Resources', 'ResourceIcon')
#------------------------------------------------------------------------------#
# Resources                                                                    #
#------------------------------------------------------------------------------#
Resources = {
#------------------------------------------------------------------------------#
# Main Window                                                                  #
#------------------------------------------------------------------------------#
'main_window_ui' : r"""<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkWindow" id="window">
    <property name="title">maggot-dict</property>
    <property name="icon_name">gnome-dictionary</property>
    <child>
      <object class="GtkBox" id="main_box">
        <property name="orientation">vertical</property>
        <child>
          <object class="GtkToolbar" id="toolbar">
            <style>
              <class name="primary-toolbar"/>
            </style>
            <property name="show_arrow">False</property>
            <property name="icon_size">1</property>
            <child>
              <object class="GtkToolButton" id="prefs_button">
                <property name="stock-id">gtk-preferences</property>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="homogeneous">True</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
            <object class="GtkBox" id="word_box">
                <property name="orientation">vertical</property>
                <property name="margin">3</property>
                <property name="spacing">3</property>
                <child>
                  <object class="GtkBox" id="entry_box">
                    <child>
                      <object class="GtkEntry" id="entry">
                      </object>
                      <packing>
                        <property name="expand">True</property>
                        <property name="fill">True</property>
                        <property name="padding">3</property>
                      </packing>
                    </child>
                    <child>
                      <object class="GtkButton" id="translate_button">
                        <property name="label">Translate</property>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                      </packing>
                    </child>
                  </object>
                  <packing>
                    <property name="expand">False</property>
                    <property name="position">1</property>
                  </packing>
                </child>
                <child>
                  <object class="GtkBox" id="grid_box" />
                  <packing>
                    <property name="expand">True</property>
                    <property name="fill">True</property>
                    <property name="position">2</property>
                  </packing>
                </child>
            </object>
            <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
            </packing>
        </child>
      </object>
    </child>
  </object>
  <object class="GtkListStore" id="list_store">
    <columns>
      <column type="gchararray"/>
    </columns>
  </object>
  <object class="GtkAdjustment" id="list_adjust">
    <property name="lower">0</property>
    <property name="upper">1</property>
    <property name="step-increment">1</property>
  </object>
</interface>
""",
#------------------------------------------------------------------------------#
# Preferences Window                                                           #
#------------------------------------------------------------------------------#
'prefs_window_ui' : r"""<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkWindow" id="window">
    <property name="width_request">300</property>
    <property name="height_request">350</property>
    <property name="title">maggot-dict preferences</property>
    <child>
      <object class="GtkBox" id="window_box">
        <property name="orientation">vertical</property>
        <property name="margin">12</property>
        <property name="spacing">12</property>
        <child>
          <object class="GtkHButtonBox" id="button_box">
            <property name="layout-style">end</property>
            <child>
              <object class="GtkButton" id="ok_button">
                <property name="label">Ok</property>
              </object>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="pack-type">end</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
</interface>
""",
#------------------------------------------------------------------------------#
# Card Window                                                                  #
#------------------------------------------------------------------------------#
'card_window_ui' : r"""<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkTextBuffer" id="buffer" />
  <object class="GtkWindow" id="window">
    <property name="title">card</property>
    <property name="width_request">400</property>
    <property name="height_request">450</property>
    <child>
      <object class="GtkBox" id="box">
        <property name="orientation">vertical</property>
        <child>
          <object class="GtkToolbar" id="toolbar">
            <style>
              <class name="primary-toolbar"/>
            </style>
            <property name="show_arrow">False</property>
            <property name="icon_size">1</property>
            <child>
              <object class="GtkToggleToolButton" id="fold_toggle">
                <property name="icon_name">format-text-underline</property>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="homogeneous">True</property>
              </packing>
            </child>
            <child>
              <object class="GtkToolButton" id="debug">
                <property name="icon_name">system-run-symbolic</property>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="homogeneous">True</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <object class="GtkScrolledWindow" id="view_window">
            <property name="hscrollbar_policy">never</property>
            <property name="vscrollbar_policy">always</property>
            <child>
              <object class="GtkTextView" id="view">
                <property name="buffer">buffer</property>
                <property name="editable">False</property>
                <property name="left_margin">5</property>
                <property name="wrap_mode">word</property>
                <property name="cursor_visible">False</property>
              </object>
            </child>
          </object>
          <packing>
            <property name="expand">True</property>
            <property name="fill">True</property>
            <property name="position">1</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
</interface>
""",
#------------------------------------------------------------------------------#
# Icons                                                                        #
#------------------------------------------------------------------------------#
'edit_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="M 0,601 0,151 Q 0,120 12,92.5 24,65 44,45 64,25 92,13 119,1 150,1 l 525,0 q 2,0 5,0.5 3,0.5 5,0.5 l -93,93 -442,0 q -23,0 -39,17 -17,16 -17,39 l 0,450 q 0,23 17,40 16,16 39,16 l 525,0 q 23,0 40,-16 16,-17 16,-40 V 384 l 94,-94 v 311 q 0,31 -12,58 -12,27 -32,48 -21,20 -48,32 -27,12 -58,12 l -525,0 Q 119,751 92,739 64,727 44,707 24,686 12,659 0,632 0,601 z M 308,593 361,432 679,114 787,222 469,540 z M 423,444 q 3,4 8,4 5,0 8,-4 L 689,195 q 9,-9 0,-17 -9,-8 -17,0 L 423,427 q -9,9 0,17 z M 733,60 778,14 q 14,-14 33,-14 19,0 32,14 l 22,22 22,22 q 13,14 14,32.5 0,18.5 -14,32.5 l -46,45 z" />
</svg>
""",
'pin_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="M 899,289 Q 895,251 878,208 861,166 831,126 801,85.5 766,57 730,28.5 694,14 658,-0.483 626,0.017 593,0.517 569,18.5 544,36.5 535,68 525,99.5 529,139 L 388,244 q -52,-29 -101,-34 -50,-4 -85,22 -25,19 -37,50 -13,32 -12,71 1,39 15,83 13,45 39,89 L 6.02,718 q -5,5 -5.996,12 -1,7 3.996,12 5,8 14.98,8 3,0 9,-2 L 270,610 q 35,37 74,63 38,26 75,38 37,12 71,9 34,-2 60,-22 35,-26 45,-75 10,-48 -4,-106 L 732,411 q 36,15 69,15 33,0 58,-18 24,-18 34,-50 10,-31 6,-69 z m -79,43 q -1,8 -8,13 -8,7 -22,7 -15,0 -31,-8 -17,-8 -34,-22 -17,-14 -33,-32 -17,-17 -32,-37 -5,-6 -4,-14 1,-7 8,-12 6,-5 14,-4 7,1 12,8 37,49 66,67 28,19 34,17 6,-5 14,-4 7,1 12,8 5,6 4,13 z M 681,382 511,509 q -6,4 -11,4 -10,0 -15,-8 -5,-6 -4,-14 1,-7 7,-12 L 651,358 q 15,14 30,24 z M 507,609 q 10,16 -4,27 -13,10 -33,10 -19,0 -41,-10 -22,-10 -44,-27 -23,-17 -45,-39 -22,-22 -41,-47 -5,-7 -4,-15 1,-7 8,-12 6,-5 14,-4 7,2 12,8 24,32 48,54 24,23 45,36 21,13 37,17 15,4 22,-2 6,-5 14,-4 7,2 12,8 z" />
</svg>
""",
'link_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="M 0,591 V 148 Q 0,117 12,89.9 24,62.8 44,43.1 64,23.4 91.5,11.6 119,-0.254 150,-0.254 h 284 q -1,6.904 -2,13.354 -1,6.4 -1,14.2 v 42.4 q 0,10.9 3,22.7 H 150 q -23,0 -39,16.6 -17,16 -17,39 v 443 q 0,23 17,39 16,16 39,16 h 525 q 23,0 40,-16 16,-16 16,-39 V 428 q 20,14 44,23 24,9 50,10 v 130 q 0,31 -12,57 -12,27 -32,47 -21,20 -48,32 -27,12 -58,12 H 150 Q 119,739 91.5,727 64,715 44,695 24,675 12,648 0,622 0,591 z M 338,488 q 0,-12 8,-20 L 722,96.4 H 591 q -12,0 -20,-7.9 -8,-7.9 -8,-19.7 V 27.3 q -1,-10.8 8,-19.17 8,-8.384 20,-8.384 h 281 q 11,0 20,8.384 8,8.37 8,19.17 V 68.8 304 q 0,12 -8,21 -9,8 -20,7 h -42 q -12,0 -20,-8 -8,-8 -8,-20 V 175 L 425,546 q -8,8 -20,8 -12,0 -20,-8 l -39,-39 q -8,-7 -8,-19 z" />
</svg>
""",
'cogs_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="m 0,356 v -84 q 0,-6 5,-6 14,-4 29.5,-6 15.5,-2 30.5,-4 4,0 7,0 3,-1 7,-1 6,-21 17,-42 -9,-13 -20,-27 -11,-14 -23,-28 -5,-5 0,-9 14,-17 30,-34 16,-16 33,-29.9 6,-4 9,1 8,7.9 17,13.9 9,7 18,14 l 21,15 q 21,-11 42,-17 2,-21 5,-38.9 2,-17.9 6,-34.8 0,-5 6,-5 h 84 q 7,0 7,6 2,13.9 5,28.4 2,14.4 4,29.3 l 2,15 q 20,6 41,17 8,-7 19,-14 10,-8 20,-15 9,-7 18,-14.9 6,-4 9,1 5,3.9 9,7.9 l 8,8 22,22 q 12,12 23,25 3,5 0,9 -10,11 -20,24 -10,14 -23,30 6,11 11,22 4,11 8,22 8,2 18,3 9,1 19,3 l 18,2 q 9,1 17,3 6,2 6,7 v 84 q 0,5 -5,7 -14,3 -29,5 -16,2 -31,4 -4,0 -14,2 -6,20 -17,40 9,14 20,28 11,14 23,28 4,5 0,9 -14,17 -30,33 -16,17 -33,31 -6,4 -9,-1 -8,-7 -17,-14 -9,-7 -18,-13 -5,-5 -10,-8 -6,-4 -11,-8 -21,11 -42,17 -2,17 -4,36 -2,20 -7,38 -2,5 -7,5 h -84 q -6,0 -6,-5 -3,-14 -5,-29 l -4,-30 -2,-15 q -20,-6 -41,-17 -5,4 -9,7 -5,3 -10,7 -10,8 -19,15 -10,7 -19,15 -6,4 -9,-1 -5,-4 -8,-8 l -9,-8 Q 88,517 76.5,506 65,495 54,481 50,477 54,473 66,459 76.5,445 87,430 96,417 86,398 78,374 70,372 60.5,371 51,370 41,368 l -18,-2 q -9,-1 -18,-3 -5,-2 -5,-7 z m 197,-41 q 0,35 25,60 25,25 60,25 35,0 60,-25 25,-25 25,-60 0,-35 -25,-60 -25,-25 -60,-25 -35,0 -60,25 -25,25 -25,60 z m 327,243 q -2,-6 4,-8 11,-4 21,-8 10,-4 21,-8 1,-5 2,-9 0,-4 2,-9 2,-5 4,-8 1,-4 3,-9 -7,-10 -13,-19 -6,-10 -12,-20 -3,-5 2,-8 l 62,-55 q 4,-4 9,-1 9,7 18,14 8,6 17,14 18,-7 35,-8 5,-10 11,-20 5,-10 10,-19 3,-5 8,-3 l 80,25 q 5,2 5,8 -2,10 -4,21 -2,10 -4,21 8,6 14,13 6,7 11,15 12,-1 23,-1 11,-1 22,-1 5,0 7,5 l 18,83 q 2,5 -4,7 -11,5 -21,8 -10,4 -21,8 -1,5 -1,9 -1,4 -3,9 -2,5 -3,8 -2,4 -4,7 7,10 14,20 6,9 11,19 2,5 -2,8 l -62,57 q -4,4 -9,0 -8,-7 -17,-14 -9,-7 -17,-14 -20,7 -37,8 -5,11 -10,21 -5,10 -10,19 -3,5 -8,3 l -80,-25 q -5,-2 -5,-8 2,-11 4,-22 1,-11 3,-22 -14,-12 -24,-27 -12,2 -23,3 -12,0 -23,-1 -5,0 -7,-5 z m 36,-417 q 0,-5 5,-7 10,-2 20,-5 10,-2 20,-4 2,-4 3,-8 1,-4 3,-8 2,-4 5,-7 2,-3 4,-7 -5,-9.9 -9,-19.4 -4,-9.4 -8,-18.4 -2,-4 2,-8 L 669,7.44 q 5,-2.98 8,1 8,6.96 15,14.46 6,7.4 13,15.4 16,-3 33,-3 12,-17.9 24,-32.84 3,-2.981 8,-1.986 L 839,34.3 q 5,3 3,8 -2,9.9 -5,18.9 -4,8.9 -7,18.9 10,12.9 18,28.9 11,1 22,1 10,1 20,3 5,2 5,6 l 5,77 q 0,4 -5,6 -10,1 -19,4 -10,2 -21,4 -2,4 -3,8 -1,3 -3,7 -3,7 -8,14 5,10 9,20 4,9 8,18 2,5 -3,8 l -63,42 q -5,3 -8,-1 -13,-12 -28,-30 -8,2 -16,3 -9,1 -18,0 -6,9 -12,17 -6,9 -12,17 -3,3 -8,1 l -69,-34 q -5,-2 -3,-7 3,-10 6,-19 3,-10 7,-20 -6,-6 -10,-13 -5,-7 -9,-15 -11,-1 -21,-1 -11,-1 -21,-3 -5,0 -5,-6 z m 98,402 q -7,22 4,42 10,21 33,28 22,7 43,-3 20,-10 27,-33 8,-22 -2,-43 -11,-20 -34,-28 -22,-7 -42,4 -21,10 -29,33 z m 23,-359 q 7,19 26,29 20,9 40,3 20,-7 29,-25 10,-20 3,-40 -7,-20 -26,-29 -19,-10 -39,-3 -20,7 -30,26 -10,19 -3,39 z" />
</svg>
""",
'speaker_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="m 349,367 c 8,-7 11,-17 10,-30 0,-13 -4,-27 -12,-44 -7,-17 -18,-34 -31,-53 -14,-19 -30,-37 -48,-55 -18,-18 -36,-34 -55,-48 -19,-13 -37,-24 -53,-31 -17,-7.5 -31,-11.5 -45,-12.1 -13,-0.7 -23,2.3 -29.7,9.1 -4.7,5 -11.5,13 -20.5,25 -9,13 -18,27 -27,44 -9,17 -17.2,36 -24.5,56 -7.35,21 -11.85,42 -13.513,63 -1.667,21 0.333,42 6.003,63 5.71,21 17.51,41 35.51,58 17.3,18 36.5,30 57.5,35 21.2,6 42.2,8 63.2,6 22,-1 42,-6 63,-13 20,-7 39,-16 56,-25 17,-9 31,-19 43,-28 12,-9 21,-15 25,-20 z M 110,136 c 2,-2 7,-2 16,-1 8,2 18,6 31,11 12,6 26,14 41,24 16,11 31,24 46,39 16,15 28,31 39,46 10,15 18,29 24,41 5,13 9,23 11,31 1,9 1,14 -1,16 -2,2 -7,2 -15,0 -9,-1 -19,-5 -31,-11 -13,-5 -26,-13 -42,-24 -15,-10 -30,-23 -46,-38 -15,-15 -28,-31 -38,-46 -11,-15 -19,-29 -25,-42 -6,-12 -9,-22 -11,-31 -1,-8 -1,-13 1,-15 z m 197,-4 c 0,7 3,13 7,18 6,5 12,8 18,8 7,0 13,-3 17,-8 l 48,-48 c 6,-5.5 8,-11.3 8,-17.6 0,-6.4 -2,-12.2 -8,-17.5 -5,-5.4 -11,-8 -18,-8 -6,0 -12,2.6 -17,8 L 314,114 c -4,5 -7,11 -7,18 z m 62,90 c 4,6 9,10 15,12 7,2 13,1 19,-2 l 48,-27 c 6,-3 10,-8 12,-15 1,-7 1,-13 -3,-19 -3,-6 -8,-10 -15,-12 -6,-2 -13,-1 -19,2 l -48,27 c -8,5 -13,13 -13,22 0,5 2,9 4,12 z M 293,2.86 c -6,-3.337 -12,-4 -19,-2.003 C 268,2.86 263,6.86 259,12.9 l -27,48 c -2,4 -3,8 -3,12 0,10.6 5,18 13,22 6,3.3 13,4.1 19,2.5 7,-1.7 12,-5.5 15,-11.5 l 27,-49 c 4,-6 4,-12.4 2,-19 -2,-6.7 -6,-11.71 -12,-15.04 z"/>
</svg>
""",
'upload_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="m 905,0.429 q 41,0 70,30.071 25,29.1 25,70.5 v 602 q 0,41 -25,70 -29,29 -70,29 H 704 V 704 H 906 V 241 H 100 v 463 h 201 v 98 H 100 Q 59.5,802 29.8,773 0.165,744 0.165,703 V 101 Q 0.165,59.6 29.8,30.5 59.5,0.429 100,0.429 H 905 z M 130,168 q 16,0 26,-11 11,-11 11,-27 0,-15 -11,-25 -10,-10.3 -26,-10.3 -16,0 -27,10.3 -9.4,10 -9.4,25 0,16 9.4,27 11,11 27,11 z m 100,0 q 17,0 28,-11 11,-11 11,-27 0,-15 -11,-25 -11,-10.3 -28,-10.3 -16,0 -27,10.3 -10,10 -10,25 0,16 10,27 11,11 27,11 z m 676,-6 V 99.9 H 301 V 162 H 906 z M 500,360 743,602 H 593 V 903 H 407 V 602 H 257 z" />
</svg>
""",
'archive_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="m 837,147 v 50 H 142 v -50 q 0,-22 12,-35 13,-12 25,-12.6 l 12,-1 h 597 q 2,0 5,0 4,0 12,1.6 8,3 14,7 7,5 12,15 6,11 6,25 z M 688,-0.577 q 2,0 5,0 4,1 12,3.007 9,3 15,6.99 7,4.98 12,14.98 6,11.1 6,25.1 H 241 q 0,-22 12,-35.1 13,-11.97 26,-12.98 l 12,-1.997 H 688 z M 937,197 l 13,13 q 10,9 13,12 3,4 8,12 6,9 7,16 1,8 1,20 0,13 -3,28 l -22,126 -36,208 q -19,109 -20,116 -4,24 -18,36 -15,13 -29,14 l -14,1 H 142 q -7,0 -16,-1 -9,-1 -26,-14 -15.1,-12 -19.1,-36 -1,-7 -20,-116 L 24.9,424 2.94,298 q -2.989,-15 -2.989,-28 0,-12 0.996,-20 1.003,-7 6.503,-16 5.45,-8 8.45,-12 3,-3 13,-12 l 13,-13 30,-30 v 80 H 907 V 167 z M 688,468 V 368 h -70 v 80 H 360 v -80 h -69 v 100 q 0,2 0,5 1,4 3,12 3,9 6,15 5,7 15,12 11,6 25,6 h 298 q 22,0 34,-13 13,-12 14,-25 z" />
</svg>
""",
'bell_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="m 316,183 c 6,14 13,22 21,27 7,4 14,8 22,11 7,3 15,7 22,11 7,5 12,14 17,27 3,10 2,23 -4,37 -7,14 -17,29 -32,44 -15,14 -33,28 -54,42 -22,14 -47,26 -74,36 -27,10 -54,17 -79,20 -25,4 -48,4 -69.1,2 -21,-2 -38,-6 -51,-12 -14,-7 -23,-15 -26,-25 -5,-13 -6,-24 -3,-33 2,-7 5,-15 9,-22 4,-6 7,-14 10,-22 3,-9 2,-20 -1,-34 -9,-33 -15,-62 -19,-86 -4.998,-24 -6,-45 -3.998,-64 C 1.9,123 6.9,106 15.9,91.1 c 9,-15 22,-30.3 40,-46.3 7,-5 11,-10 12,-13.7 1,-4.9 2,-8.9 3,-11.9 1,-4 2,-7 3,-10 1,-3 5,-6 12,-8 6,-1.998 10,-1.998 13,-0.998 C 103,1.2 105,3.2 108,5.2 c 3,3 6,5.1 10,8 4,2 10,3 18,3 23,0 43,2 60,8 16,5.9 31,15.6 44,28.6 13,14.3 25,31.3 37,52.2 12,22 25,48 39,78 z m -93,202 c 24,-9 45,-18 64,-30 18,-12 33,-23 45,-35 11,-11 19,-21 24,-30 6,-9 9,-16 8,-19 -1,-4 -7,-8 -16,-12 -8,-3 -19,-5 -34,-6 -15,0 -34,1 -55,5 -21,4 -46,11 -74,22 -28,10 -51,21 -70,32 -19.1,12 -34.1,22 -45.1,32 -11,11 -19,20 -23,27 -4,9 -5,15 -4,19 1,3 6,6 16,9 9,3 22,5 38,6 17.1,1 36.1,0 58.1,-2 21,-3 44,-9 68,-18 z m -31,-86 c 3,-1 7,-2 10,-3 3,-1 6,-2 9,-4 v 1 c 5,14 2,27 -8,41 -10,13 -25,24 -44,31 -15,5 -30,7 -43,5 -14,-1 -25.1,-5 -33.1,-12 11,-9 26.1,-19 44.1,-29 18,-11 40,-20 65,-30 z" />
</svg>
""",
'feather_icon' : br"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <path d="m 857,1.4 q 71,5.01 101,16.1 30,11 25,26 -5,14.1 -21,28.1 L 930,104 q -19,18 -18,30 2,14 -11,47 -13,32 -29,51 -10,12 -95,29 -85,16 -166,27 l -80,11 q 13,7 37,19 23,12 96,33 71,21 141,27 -26,38 -80,66 -55,28 -116,40 -60,12 -116,19 -56,6 -93,6 h -36 l 12,11 q 7,7 31,24 24,16 50,29 26,12 66,21 39,9 78,6 -2,2 -19,17 -17,13 -26,19 l -31,21 q -21,14 -39,21 l -42,17 q -26,10 -51,13 -26,2 -57,3 -31,1 -65,-5 -34,-7 -70,-19 L 52.1,934 q -7,9 -21.6,10 Q 16,944 5.43,932 -5.1,920 2.93,903 L 125,636 Q 201,471 272,361 342,250 472,121 547,45.5 641,19.5 733,-7.64 857,1.4 z" />
</svg>
"""
}

#------------------------------------------------------------------------------#
# Resource Icon                                                                #
#------------------------------------------------------------------------------#
from gi.repository import Gio, GdkPixbuf
def ResourceIcon (name, size = None):
    resource = Resources.get (name + '_icon')
    if resource is None:
        raise ValueError ('No such resource: \'{}\''.format (name))

    stream = Gio.MemoryInputStream.new_from_data (resource, None)
    if size is None:
        return GdkPixbuf.Pixbuf.new_from_stream (stream, None)
    return GdkPixbuf.Pixbuf.new_from_stream_at_scale (stream, size, size, True, None)
# vim: nu ft=python columns=120 :
