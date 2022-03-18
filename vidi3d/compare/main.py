"""
Sets up the main window for the compare viewer. Creates MplImage, MplPlot, 
and ControlWidget objects and connects their Qt Signals to local functions.
"""
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore, QtWidgets
from matplotlib import path
from matplotlib.animation import FuncAnimation

from . import controls
from .. import core
from ..coordinates import XYZTCoord, XYZCoord
from ..definitions import ImageDisplayType, PlotColours
from ..helpers import apply_display_type
from ..image import MplImage
from ..navigation import NavigationToolbar
from ..plot import MplPlot


class Compare(QtWidgets.QMainWindow):
    def __init__(self,
                 complex_images,
                 background_threshold=0.05,
                 pixdim=None,
                 interpolation='bicubic',
                 origin='lower',
                 subplot_titles=None,
                 location_labels=None,
                 max_in_row=None,
                 cmaps=[None, ],
                 overlays=[None, ],
                 overlay_cmaps=[None, ],
                 mmb_callback=None
                 ):
        super().__init__()
        self.setWindowTitle('Vidi3d: compare')
        self.viewer_number = 0

        def broadcast_singleton(singleton, in_list):
            list_len = len(in_list)
            out_list = singleton
            if len(singleton) == 1 and list_len > 1:
                out_list = singleton * list_len
            return out_list

        self.complex_images = complex_images
        cmaps = broadcast_singleton(cmaps, complex_images)

        self.overlays = broadcast_singleton(overlays, complex_images)
        enable_overlay = not all(v is None for v in overlays)
        overlay_range = [0, 0]
        if enable_overlay:
            mins = [np.ma.masked_invalid(overlay).min() for overlay in self.overlays if overlay is not None]
            maxs = [np.ma.masked_invalid(overlay).max() for overlay in self.overlays if overlay is not None]
            overlay_range = [np.min(mins), np.max(maxs)]
        overlay_cmaps = broadcast_singleton(overlay_cmaps, self.overlays)

        # a few image parameters
        num_images = len(self.complex_images)
        img_shape = self.complex_images[0].shape
        display_type = ImageDisplayType.mag
        aspect = 'equal' if pixdim is None else np.float(pixdim[1]) / pixdim[0]
        self.pixdim = pixdim

        # initial cursor_loc
        self.loc = XYZTCoord(img_shape, int(img_shape[0] / 2), int(img_shape[1] / 2), int(img_shape[2] / 2), 0)

        # ensure each image has a title
        if type(subplot_titles) is list and len(subplot_titles) != 1 and len(subplot_titles) != num_images:
            subplot_titles = None
        if num_images == 1 and subplot_titles in (None, [None]):
            subplot_titles = [""]
        elif num_images > 1 and isinstance(subplot_titles, list) and len(subplot_titles) == 1 and isinstance(
                subplot_titles[0], str):
            subplot_titles = [f'{subplot_titles[0]} {i}' for i in range(num_images)]
        elif type(subplot_titles) is list and subplot_titles != [None]:
            pass
        else:
            subplot_titles = [f'Image {i}' for i in range(num_images)]
        self.subplot_titles = subplot_titles

        # Set up image panels and toolbars
        self.image_panel_widget = QtWidgets.QWidget(self)
        colors = PlotColours.colours
        self.image_figures = []
        self.image_toolbars = []
        if location_labels is None:
            location_labels = ["X", "Y", "Z", "T"]
        for indx in range(num_images):
            labels = [{'color': 'r', 'textLabel': location_labels[0]},
                      {'color': 'b', 'textLabel': location_labels[1]},
                      {'color': colors[indx], 'textLabel': subplot_titles[indx]},
                      ]
            overlay = self.overlays[indx][:, :, self.loc.z] if self.overlays[indx] is not None else None
            self.image_figures.append(
                MplImageSlice(complex_image=self.complex_images[indx][:, :, self.loc.z, self.loc.t],
                              background_threshold=background_threshold,
                              aspect=aspect,
                              interpolation=interpolation,
                              origin=origin,
                              cursor_loc=self.loc,
                              display_type=display_type,
                              cursor_labels=labels,
                              cmap=cmaps[indx],
                              overlay=overlay,
                              overlay_cmap=overlay_cmaps[indx],
                              mmb_callback=mmb_callback,
                              ))
            self.image_toolbars.append(NavigationToolbar(self.image_figures[indx], self.image_figures[indx], indx))
            # give MplImageSlice a new attribute NavigationToolbar
            self.image_figures[-1].NavigationToolbar = self.image_toolbars[-1]

        # Layout image panels in a grid
        self.image_panel_layout = QtWidgets.QGridLayout()
        imgs_layout = self.image_panel_layout
        if max_in_row is None:
            max_in_row = int(np.sqrt(num_images) + 1 - 1e-10)
        for indx in range(num_images):
            imgs_layout.addWidget(self.image_toolbars[indx], 2 * np.floor(indx / max_in_row), indx % max_in_row)
            imgs_layout.addWidget(self.image_figures[indx], 2 * np.floor(indx / max_in_row) + 1, indx % max_in_row)
        self.image_panel_widget.setLayout(imgs_layout)

        # Set up Controls
        self.control_widget = controls.CompareControlWidget(img_shape=img_shape,
                                                            location=self.loc,
                                                            location_labels=location_labels,
                                                            img_vals=list(
                                                                zip(subplot_titles,
                                                                    [i.cursor_val for i in self.image_figures])),
                                                            overlay_range=overlay_range,
                                                            )
        if not enable_overlay:
            self.control_widget.overlay_threshold_widget.setEnabled(False)

        # Set up ROI
        self.roi_data = ROIData()

        # Set up Movie
        num_frames = self.complex_images[0].shape[-1]
        init_interval = self.control_widget.movie_interval_spinbox.value()
        self.movie_player = FuncAnimationCustom(self.image_figures[0].fig,
                                                self.movie_update,
                                                frames=range(num_frames),
                                                interval=init_interval,
                                                blit=True,
                                                repeat_delay=0,
                                                )
        self.current_movie_frame = 0

        # Set up plots
        self.plots_panel_widget = QtWidgets.QWidget(self)
        self.plots = []
        x_plot_data = []
        y_plot_data = []
        z_plot_data = []
        t_plot_data = []
        for img in self.complex_images:
            x_plot_data.append(img[:, self.loc.y, self.loc.z, self.loc.t])
            y_plot_data.append(img[self.loc.x, :, self.loc.z, self.loc.t])
            z_plot_data.append(img[self.loc.x, self.loc.y, :, self.loc.t])
            t_plot_data.append(img[self.loc.x, self.loc.y, self.loc.z, :])
        self.xplot = MplPlot(complex_data=x_plot_data,
                             title=location_labels[0],
                             display_type=display_type,
                             colors=colors,
                             init_marker=self.loc.y,
                             )
        self.plots.append(self.xplot)
        self.yplot = MplPlot(complex_data=y_plot_data,
                             title=location_labels[1],
                             display_type=display_type,
                             colors=colors,
                             init_marker=self.loc.x
                             )
        self.plots.append(self.yplot)
        self.zplot = MplPlot(complex_data=z_plot_data,
                             title=location_labels[2],
                             display_type=display_type,
                             colors=colors,
                             init_marker=self.loc.z
                             )
        self.plots.append(self.zplot)
        self.tplot = MplPlot(complex_data=t_plot_data,
                             title=location_labels[3],
                             display_type=display_type,
                             colors=colors,
                             init_marker=self.loc.t
                             )
        self.plots.append(self.tplot)
        plots_panel_layout = QtWidgets.QVBoxLayout()
        plots_panel_layout.addWidget(self.xplot)
        plots_panel_layout.addWidget(self.yplot)
        plots_panel_layout.addWidget(self.zplot)
        plots_panel_layout.addWidget(self.tplot)
        self.plots_panel_widget.setLayout(plots_panel_layout)

        # make each section resizeable using a splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter = self.splitter
        splitter.addWidget(self.control_widget)
        splitter.addWidget(self.image_panel_widget)
        splitter.addWidget(self.plots_panel_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)

        # used when inheriting from QMainWindow
        self.setCentralWidget(splitter)
        # self.statusBar().showMessage('Ready')

        self.make_connections()

        self.show()
        self.setFocus()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def make_connections(self):
        # Connect signals from control_widget
        self.control_widget.sig_img_disp_type_change.connect(self.change_display_type)
        # todo: loc set multiple times
        self.control_widget.sig_cursor_change.connect(self.change_location)
        self.control_widget.sig_z_change.connect(self.on_z_change)
        self.control_widget.sig_lock_plots_change.connect(self.update_plot_lock)
        self.control_widget.sig_window_level_change.connect(self.change_window_level)
        self.control_widget.sig_window_level_reset.connect(self.set_window_level_to_default)
        self.control_widget.sig_t_change.connect(self.on_t_change)
        self.control_widget.sig_roi_clear.connect(self.clear_roi)
        self.control_widget.sig_roi_del_last.connect(self.delete_last_roi)
        self.control_widget.sig_roi_avg_timecourse.connect(self.plot_roi_avg_timeseries)
        self.control_widget.sig_roi_psc_timecourse.connect(self.plot_roi_psc_timeseries)
        self.control_widget.sig_roi_1vol_histogram.connect(self.plot_roi_1vol_histogram)
        self.control_widget.sig_movie_interval_change.connect(self.change_movie_interval)
        self.control_widget.sig_movie_pause.connect(self.pause_movie)
        self.control_widget.sig_movie_goto_frame.connect(self.movie_goto_frame)
        self.control_widget.sig_overlay_lower_thresh_change.connect(self.threshold_overlay)
        self.control_widget.sig_overlay_upper_thresh_change.connect(self.threshold_overlay)
        self.control_widget.sig_overlay_alpha_change.connect(self.set_overlay_alpha)

        # Connect signals from imagePanel
        for image_figure in self.image_figures:
            image_figure.sig_cursor_change.connect(self.change_location)
            image_figure.sig_window_level_change.connect(self.change_window_level)
            image_figure.sig_z_change.connect(self.on_z_change)

        # Connect signals from imagePanel toolbars
        for image_toolbar in self.image_toolbars:
            image_toolbar.sig_roi_init.connect(self.initialize_roi)
            image_toolbar.signal_roi_destruct.connect(self.destruct_roi)
            image_toolbar.sig_roi_start.connect(self.start_new_roi)
            image_toolbar.sig_roi_change.connect(self.update_roi)
            image_toolbar.sig_roi_end.connect(self.end_roi)
            image_toolbar.sig_roi_cancel.connect(self.cancel_roi)
            image_toolbar.sig_movie_init.connect(self.initialize_movie)
            image_toolbar.sig_movie_destruct.connect(self.destruct_movie)

    def set_viewer_number(self, number):
        self.viewer_number = number

    # todo: slot naming convention?
    # slots dealing with image appearance
    def change_display_type(self, display_type):
        self.control_widget.set_display_type(display_type)
        self.xplot.show_data_type_change(display_type)
        self.yplot.show_data_type_change(display_type)
        self.zplot.show_data_type_change(display_type)
        self.tplot.show_data_type_change(display_type)

        for image_figure in self.image_figures:
            image_figure.show_display_type_change(display_type)

    def keyPressEvent(self, event):
        key = event.key()
        if key == 77:
            self.change_display_type(ImageDisplayType.mag)
        elif key == 80:
            self.change_display_type(ImageDisplayType.phase)
        elif key == 82:
            self.change_display_type(ImageDisplayType.real)
        elif key == 73:
            self.change_display_type(ImageDisplayType.imag)
        event.ignore()

    def change_window_level(self, new_window, new_level):
        self.control_widget.change_window_level(new_window, new_level)
        for image_figure in self.image_figures:
            image_figure.show_window_level_change(new_window, new_level)

    def set_window_level_to_default(self):
        self.control_widget.change_window_level(0, 0)
        for image_figure in self.image_figures:
            image_figure.show_set_window_level_to_default()

    # slots dealing with a cursor_loc change
    def change_location(self, x, y):
        # todo: loc set multiple times: location already changed in control
        self.loc.x = x
        self.loc.y = y
        self.control_widget.change_location(x, y)
        self.update_plots()
        self.update_display_values()

    def update_display_values(self):
        num_images = len(self.image_figures)
        img_vals = []
        for indx in range(num_images):
            # todo: loc set multiple times: show_cursor_loc_change also changes loc object
            self.image_figures[indx].show_cursor_loc_change([self.loc.x, self.loc.y])
            img_vals.append(self.image_figures[indx].cursor_val)
        self.control_widget.change_img_vals(img_vals)

    def on_z_change(self, newz):
        prevz = self.loc.z
        self.loc.z = newz
        self.control_widget.change_z_location(newz)

        drawing_engaged = False
        for image_toolbar in self.image_toolbars:
            if image_toolbar.roi_drawing_engaged:
                drawing_engaged = True
                image_toolbar.roi_drawing_engaged = False
        for image_toolbar in self.image_toolbars:
            if image_toolbar.roi_active:
                if prevz in image_toolbar.roi_lines.mpl_line_objects:
                    for currentLine in image_toolbar.roi_lines.mpl_line_objects[prevz]:
                        image_toolbar.ax.lines.remove(currentLine)
            if drawing_engaged:
                image_toolbar.roi_lines.mpl_line_objects[prevz].pop()

        for image_toolbar in self.image_toolbars:
            if image_toolbar.roi_active:
                if newz in image_toolbar.roi_lines.mpl_line_objects:
                    for currentLine in image_toolbar.roi_lines.mpl_line_objects[newz]:
                        image_toolbar.ax.add_line(currentLine)

        for image_figure in self.image_figures:
            image_figure.cursor_loc.z = newz
        for indx in range(len(self.image_figures)):
            self.image_figures[indx].show_complex_image_change(self.complex_images[indx][:, :, self.loc.z, self.loc.t])
            self.threshold_overlay(self.control_widget.lower_thresh_spinbox.value(),
                                   self.control_widget.upper_thresh_spinbox.value())
        self.update_plots()
        self.update_display_values()

    def on_t_change(self, value):
        self.loc.t = value
        for indx in range(len(self.image_figures)):
            self.image_figures[indx].show_complex_image_change(
                self.complex_images[indx][:, :, self.loc.z, self.loc.t])
        self.update_plots()
        self.update_display_values()

    def update_plots(self):
        x_plot_data = []
        y_plot_data = []
        z_plot_data = []
        t_plot_data = []
        for img in self.complex_images:
            x_plot_data.append(img[:, self.loc.y, self.loc.z, self.loc.t])
            y_plot_data.append(img[self.loc.x, :, self.loc.z, self.loc.t])
            z_plot_data.append(img[self.loc.x, self.loc.y, :, self.loc.t])
            t_plot_data.append(img[self.loc.x, self.loc.y, self.loc.z, :])

        self.xplot.show_complex_data_and_markers_change(x_plot_data, self.loc.x)
        self.yplot.show_complex_data_and_markers_change(y_plot_data, self.loc.y)
        self.zplot.show_complex_data_and_markers_change(z_plot_data, self.loc.z)
        self.tplot.show_complex_data_and_markers_change(t_plot_data, self.loc.t)

    def update_plot_lock(self):
        lock_plots = self.control_widget.lock_plots_checkbox.isChecked()
        for curr_plot in self.plots:
            curr_plot.lockPlot = lock_plots

    # slots for ROI tool
    def initialize_roi(self, img_index):
        self.control_widget.roi_analysis_widget.setEnabled(True)
        if self.image_toolbars[img_index].canvas.receivers(self.image_toolbars[img_index].canvas.sig_cursor_change) > 0:
            self.image_toolbars[img_index].canvas.sig_cursor_change.disconnect(self.change_location)

    def destruct_roi(self, img_index):
        at_least_one_active = False
        for image_toolbar in self.image_toolbars:
            if image_toolbar.roi_active:
                at_least_one_active = True
        if not at_least_one_active:
            self.control_widget.roi_analysis_widget.setEnabled(False)
        self.image_toolbars[img_index].canvas.sig_cursor_change.connect(self.change_location)

    def update_roi(self, x, y):
        curr_roi_verts = self.roi_data.verts[self.loc.z][-1]
        curr_roi_verts.append((x, y))
        for image_toolbar in self.image_toolbars:
            currentLine = image_toolbar.roi_lines.mpl_line_objects[self.loc.z][-1]
            currentLine.set_data(zip(*curr_roi_verts))
            self.draw_roi(image_toolbar)

    def draw_roi(self, image_toolbar):
        if image_toolbar.roi_active:
            # do we need to draw all these lines?
            for currentLine in image_toolbar.roi_lines.mpl_line_objects[self.loc.z]:
                image_toolbar.ax.draw_artist(currentLine)
            image_toolbar.canvas.blit(image_toolbar.ax.bbox)

    def start_new_roi(self, x, y):
        self.roi_data.start_new_lasso(x, y, self.loc.z)
        for image_toolbar in self.image_toolbars:
            image_toolbar.roi_lines.start_new_lasso_line(x, y, self.loc.z)
            if image_toolbar.roi_active:
                currentline = image_toolbar.roi_lines.mpl_line_objects[self.loc.z][-1]
                image_toolbar.ax.add_line(currentline)

    def end_roi(self):
        curr_roi_verts = self.roi_data.verts[self.loc.z][-1]
        curr_roi_verts.append(curr_roi_verts[0])
        for image_toolbar in self.image_toolbars:
            curr_line = image_toolbar.roi_lines.mpl_line_objects[self.loc.z][-1]
            curr_line.set_data(zip(*curr_roi_verts))
            self.draw_roi(image_toolbar)

    def cancel_roi(self):
        for image_toolbar in self.image_toolbars:
            curr_line = image_toolbar.roi_lines.mpl_line_objects[self.loc.z].pop()
            if image_toolbar.roi_active:
                image_toolbar.ax.lines.remove(curr_line)
                image_toolbar.canvas.draw()
        self.roi_data.verts[self.loc.z].pop()

    def get_roi_mask(self):
        mask = np.zeros(self.complex_images[0].shape[:-1], dtype='bool')
        for z in self.roi_data.verts:
            for contour in self.roi_data.verts[z]:
                mypath = path.Path(contour)
                tmp = mypath.contains_points(list(np.ndindex(self.complex_images[0].shape[:2])))
                tmp = tmp.reshape(self.complex_images[0].shape[:2])
                mask[..., z] = np.logical_or(mask[..., z], tmp)
        return mask

    def plot_roi_avg_timeseries(self):
        mask = self.get_roi_mask()
        display_type = self.image_figures[0].display_type
        fig = None
        num_active_plots = 0
        for index in range(len(self.image_toolbars)):
            image_toolbar = self.image_toolbars[index]
            if image_toolbar.roi_active:
                data = self.complex_images[index]
                data = apply_display_type(data, display_type)
                avgTimeseries = data[mask].mean(axis=0)
                if fig == None:
                    fig = plt.figure()
                plt.plot(avgTimeseries, PlotColours.colours[index], label=self.subplot_titles[index])
                num_active_plots += 1
        if not (num_active_plots <= 1 and self.subplot_titles[index] == ""):
            plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Average Signal")
        plt.show()

    def plot_roi_psc_timeseries(self):
        mask = self.get_roi_mask()
        display_type = self.image_figures[0].display_type
        fig = None
        num_active_plots = 0
        for index in range(len(self.image_toolbars)):
            image_toolbar = self.image_toolbars[index]
            if image_toolbar.roi_active:
                data = self.complex_images[index]
                data = apply_display_type(data, display_type)
                psc_timeseries = data[mask].mean(axis=0)
                psc_timeseries = psc_timeseries + np.finfo(float).eps
                psc_timeseries = (psc_timeseries - psc_timeseries[0]) / psc_timeseries[0] * 100
                if fig == None:
                    fig = plt.figure()
                plt.plot(psc_timeseries, PlotColours.colours[index], label=self.subplot_titles[index])
                num_active_plots += 1
        if not (num_active_plots <= 1 and self.subplot_titles[index] == ""):
            plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Percent Signal Change")
        plt.show()

    def plot_roi_1vol_histogram(self, num_bins):
        mask = self.get_roi_mask()
        display_type = self.image_figures[0].display_type
        data_list = []
        color_list = []
        label_list = []
        fig = False
        num_active_plots = 0
        for index in range(len(self.image_toolbars)):
            image_toolbar = self.image_toolbars[index]
            if image_toolbar.roi_active:
                data = self.complex_images[index]
                data = apply_display_type(data, display_type)
                data_list.append(data[..., self.loc.t][mask])
                color_list.append(PlotColours.colours[index])
                label_list.append(self.subplot_titles[index])
                # y,binEdges,_=plt.hist(data[...,self.cursor_loc.t][mask],bins=num_bins,color=PlotColours.colours[index], alpha=0.04)
                # bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
                # plt.plot(bincenters,y,'-',marker="s",color=PlotColours.colours[index], label=self.subplot_titles[index])
                fig = True
                num_active_plots += 1
        if fig:
            plt.figure()
            plt.hist(data_list, bins=num_bins, color=color_list, label=label_list)
            if not (num_active_plots <= 1 and self.subplot_titles[index] == ""):
                plt.legend()
        plt.show()

    def clear_roi(self):
        self.roi_data.verts = {}
        z = self.loc.z
        for image_toolbar in self.image_toolbars:
            if image_toolbar.roi_active:
                if z in image_toolbar.roi_lines.mpl_line_objects:
                    for currentLine in image_toolbar.roi_lines.mpl_line_objects[z]:
                        image_toolbar.ax.lines.remove(currentLine)
            image_toolbar.roi_lines.mpl_line_objects = {}
            image_toolbar.canvas.draw()
            image_toolbar.canvas.blit(image_toolbar.ax.bbox)

    def delete_last_roi(self):
        z = self.loc.z
        self.roi_data.verts[z].pop()
        for image_toolbar in self.image_toolbars:
            if image_toolbar.roi_active:
                if z in image_toolbar.roi_lines.mpl_line_objects:
                    curr_line = image_toolbar.roi_lines.mpl_line_objects[z][-1]
                    image_toolbar.ax.lines.remove(curr_line)
            image_toolbar.roi_lines.mpl_line_objects[z].pop()
            image_toolbar.canvas.draw()
            image_toolbar.canvas.blit(image_toolbar.ax.bbox)

    # slots for overlays thresholding
    def threshold_overlay(self, lower_thresh, upper_thresh):
        for indx in range(len(self.image_figures)):
            if self.overlays[indx] is not None:
                overlay = self.overlays[indx][:, :, self.loc.z]
                lower_thresh_mask = overlay >= lower_thresh
                upper_thresh_mask = overlay <= upper_thresh
                mask = (lower_thresh_mask * upper_thresh_mask).astype('bool')
                if self.control_widget.overlay_invert_checkbox.isChecked():
                    mask = np.invert(mask)
                thresholded = np.ma.masked_where(mask, overlay)
                self.image_figures[indx].set_overlay(thresholded)
                self.image_figures[indx].blit_image_and_lines()

    def set_overlay_alpha(self, value):
        for indx in range(len(self.image_figures)):
            if self.overlays[indx] is not None:
                self.image_figures[indx].overlay.set_alpha(value)
                self.image_figures[indx].blit_image_and_lines()

    # slots for movie tool
    def movie_update(self, frame):
        z = self.loc.z
        self.current_movie_frame = frame
        display_type = self.image_figures[0].display_type
        artists_to_update = []
        for indx in range(len(self.image_toolbars)):
            image_toolbar = self.image_toolbars[indx]
            if image_toolbar._movie_active:
                new_data = apply_display_type(self.complex_images[indx][..., z, frame].T, display_type)
                image_toolbar.movieText.set_text("frame: " + str(frame))
                self.image_figures[indx].img.set_data(new_data)
                artists_to_update.append(image_toolbar.movieText)
                artists_to_update.append(self.image_figures[indx].img)
        return artists_to_update

    def initialize_movie(self, img_index):
        num_active = 0
        for image_toolbar in self.image_toolbars:
            if image_toolbar._movie_active:
                num_active += 1
        if num_active == 1:
            self.control_widget.movie_widget.setEnabled(True)
            self.control_widget.movie_pause_button.setChecked(False)
            self.movie_player.movie_paused = False
            if not self.movie_player.movie_paused:
                self.movie_player.event_source.start()

        if self.image_toolbars[img_index].canvas.receivers(
                self.image_toolbars[img_index].canvas.sig_cursor_change) > 0:
            self.image_toolbars[img_index].canvas.sig_cursor_change.disconnect(self.change_location)
        if self.overlays[img_index] is not None:
            self.image_figures[img_index].overlay.set_visible(False)
        self.movie_player._draw_next_frame(self.current_movie_frame, True)

    def destruct_movie(self, img_index):
        at_least_one_active = False
        for image_toolbar in self.image_toolbars:
            if image_toolbar._movie_active:
                at_least_one_active = True
        if not at_least_one_active:
            self.control_widget.movie_widget.setEnabled(False)
            self.movie_player.event_source.stop()
            self.movie_player.movie_paused = True
        self.image_toolbars[img_index].canvas.sig_cursor_change.connect(self.change_location)
        if self.overlays[img_index] is not None:
            self.image_figures[img_index].overlay.set_visible(True)
        self.image_figures[img_index].show_complex_image_change(
            self.complex_images[img_index][:, :, self.loc.z, self.loc.t])

    def change_movie_interval(self, interval):
        self.movie_player._interval = interval

    def pause_movie(self):
        self.movie_player.movie_paused = self.control_widget.movie_pause_button.isChecked()
        if self.movie_player.movie_paused:
            self.movie_player.event_source.stop()
        else:
            self.movie_player.event_source.start()

    def movie_goto_frame(self, frame):
        new_frame_seq = self.movie_player.new_frame_seq()
        for i in range(frame):
            next(new_frame_seq)
        self.movie_player.frame_seq = new_frame_seq
        self.movie_player._draw_next_frame(frame, True)

    def closeEvent(self, event):
        self.movie_player.event_source.stop()
        if self.viewer_number:
            del core._open_viewers[self.viewer_number]
        event.accept()


# other classes
class ROIData():
    def __init__(self):
        self.verts = {}

    def start_new_lasso(self, x, y, z):
        if z in self.verts:
            self.verts[z].append([(x, y), ])
        else:
            self.verts[z] = [[(x, y), ], ]


class MplImageSlice(MplImage):
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.sig_z_change.emit(self.cursor_loc.z + 1)
        else:
            self.sig_z_change.emit(self.cursor_loc.z - 1)


class FuncAnimationCustom(FuncAnimation):
    def __init__(self, *args, **keywords):
        FuncAnimation.__init__(self, *args, **keywords)
        self.movie_paused = True

    def _start(self, *args):
        '''
        Starts interactive animation. Adds the draw frame command to the GUI
        handler, calls show to start the event loop.
        '''
        # First disconnect our draw event handler
        self._fig.canvas.mpl_disconnect(self._first_draw_id)
        self._first_draw_id = None  # So we can check on save

        # Now do any initial draw
        self._init_draw()

        # Add our callback for stepping the animation and
        # actually start the event_source.
        self.event_source.add_callback(self._step)
        # AK: ADDED A CHECK FOR MOVIE PAUSE
        if not self.movie_paused:
            self.event_source.start()

    def _end_redraw(self, evt):
        # Now that the redraw has happened, do the post draw flushing and
        # blit handling. Then re-enable all of the original events.
        self._post_draw(None, False)
        # AK: ADDED A CHECK FOR MOVIE PAUSE
        if not self.movie_paused:
            self.event_source.start()
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._resize_id = self._fig.canvas.mpl_connect('resize_event',
                                                       self._on_resize)

    def _blit_draw(self, artists):
        # Handles blitted drawing, which renders only the artists given instead
        # of the entire figure.
        updated_ax = {a.axes for a in artists}
        # Enumerate artists to cache axes' backgrounds. We do not draw
        # artists yet to not cache foreground from plots with shared axes
        for ax in updated_ax:
            # If we haven't cached the background for the current view of this
            # axes object, do so now. This might not always be reliable, but
            # it's an attempt to automate the process.
            cur_view = ax._get_view()
            view, bg = self._blit_cache.get(ax, (object(), None))
            if cur_view != view:
                # AK: CHANGED SO WE CAN SEE FRAME TEXT BOX REDRAWN
                # self._blit_cache[ax] = (
                #     cur_view, ax.figure.canvas.copy_from_bbox(ax.bbox))
                self._blit_cache[ax] = (
                    cur_view, ax.figure.canvas.copy_from_bbox(ax.figure.bbox))
        # Make a separate pass to draw foreground.
        for a in artists:
            a.axes.draw_artist(a)
        # After rendering all the needed artists, blit each axes individually.
        for ax in updated_ax:
            # AK: CHANGED SO WE CAN SEE FRAME TEXT BOX REDRAWN
            # ax.figure.canvas.blit(ax.bbox)
            ax.figure.canvas.blit(ax.figure.bbox)

    def _on_resize(self, *args):
        # On resize, we need to disable the resize event handling so we don't
        # get too many events. Also stop the animation events, so that
        # we're paused. Reset the cache and re-init. Set up an event handler
        # to catch once the draw has actually taken place.
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self.event_source.stop()
        self._blit_cache.clear()
        # AK: REMOVE THIS LINE SO A RESET FRAME SEQUENCE ISN'T DRAWN WHEN RESIZING
        # self._init_draw()
        self._resize_id = self._fig.canvas.mpl_connect('draw_event', self._end_redraw)
