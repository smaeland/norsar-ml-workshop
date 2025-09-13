import numpy as np
import h5py
from obspy.signal.cross_correlation import correlate_template
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, Span, CustomJS, Div, Range1d
from bokeh.models.tools import PanTool, BoxZoomTool, ResetTool, WheelZoomTool

def create_standalone_html(main_signal, templates, time_vector, sample_rate, 
                           output_filename="cross_correlation_app.html"):

    
    assert len(main_signal) > 0, f'len(main_signal) = {len(main_signal)}'

    all_cc_values = []
    for template in templates:
        
        assert len(template) > 0, f'len(template) = {len(template)}'

        all_cc_values.append(
            correlate_template(main_signal, template, mode='same')
        )

    cc_values = np.vstack(all_cc_values)
    # cc_values = np.squeeze(cc_values)
    print('cc_values.shape:', cc_values.shape)
    cc_values = np.sum(cc_values, axis=0) / len(all_cc_values)

    print('cc_values:')
    print(cc_values)

    template = templates[0] # FIX

    
    # Create time vector for cross-correlation (shifts)
    max_shift = len(main_signal) - len(template)
    cc_time = np.arange(len(cc_values)) / sample_rate
    
    # Create data sources
    # Main signal source
    main_source = ColumnDataSource(data=dict(
        time=time_vector,
        amplitude=main_signal
    ))
    
    # Template source
    template_source = ColumnDataSource(data=dict(
        time=time_vector[:len(template)],  # Initial position
        times_at_t0=time_vector[:len(template)],
        amplitude=template,
    ))
    
    # Cross-correlation source
    cc_source_sum = ColumnDataSource(data=dict(
        time=cc_time,
        correlation=cc_values
    ))
    
    cc_sources = []
    for cc_val in all_cc_values:
        cc_sources.append(
            ColumnDataSource(data=dict(
                    time=cc_time,
                    correlation=cc_val
                ))
        )
    
    # Create figures
    # Top panel: Main signal and template overlay
    p1 = figure(
        width=1200, 
        height=340, 
        title="Waveform with Template Overlay",
        x_axis_label="Time (s)",
        y_axis_label="Amplitude",
        tools=[PanTool(), BoxZoomTool(), ResetTool(), WheelZoomTool()],
        sizing_mode="fixed"
    )
    
    # Plot main signal
    p1.line('time', 'amplitude', source=main_source, 
            line_width=1, color='blue', alpha=1.0, legend_label="Signal")
    
    # Plot template (will move with slider)
    template_line = p1.line('time', 'amplitude', source=template_source, 
                           line_width=1, color='red', alpha=0.7, legend_label="Template")
    
    p1.legend.location = "top_right"
    p1.legend.click_policy = "hide"
    
    # Bottom panel: Cross-correlation
    p2 = figure(
        width=1200, 
        height=340,
        title="Cross-Correlation",
        x_axis_label="Template Position (s)",
        y_axis_label="Correlation",
        tools=[PanTool(), BoxZoomTool(), ResetTool(), WheelZoomTool()],
        x_range=p1.x_range,  # Link x-ranges
        sizing_mode="fixed"
    )
    p2.y_range = Range1d(-1, 1)
    
    # Plot cross-correlation
    colors = ['blue', 'orange', 'green', 'red', 'pink']
    for cc_source, color in zip(cc_sources, colors):
        p2.line('time', 'correlation', source=cc_source, line_width=1, color=color, alpha=0.3)

    p2.line('time', 'correlation', source=cc_source_sum, line_width=1, color='purple')
    
    # Add vertical line indicator for current template position
    vline = Span(location=(len(template)//2)/sample_rate, dimension='height', 
                 line_color='red', line_width=2, line_alpha=0.7)
    p2.add_layout(vline)
    
    # Create slider for template position
    slider = Slider(
        start=0, 
        end=max_shift,
        value=0,
        step=1,
        title="Template Position (samples)"
    )
    
    # Info div to show current correlation value
    info_div = Div(text="<b>Current Correlation:</b> 0.0000 | <b>Time:</b> 0.000 s", 
               #    width=1600, height=30
               )
    
    # JavaScript callback for slider updates
    callback = CustomJS(args=dict(
        template_source=template_source,
        cc_source=cc_source,
        vline=vline,
        slider=slider,
        info_div=info_div,
        sample_rate=sample_rate
    ), code="""
        // Get the new position
        const position = Math.floor(slider.value);
        //console.log('position:', position)
        
        const times_at_t0 = template_source.data['times_at_t0']
        const times = times_at_t0.map(item => item + (position / sample_rate));
        template_source.data['time'] = times
        template_source.change.emit();

        const center_position = position + Math.floor(times.length / 2)
        
        // Update vertical line position on cross-correlation plot
        vline.location = center_position / sample_rate;
        
        // Update info text
        const cc_values = cc_source.data['correlation'];
        if (center_position < cc_values.length) {
            const cc_val = cc_values[center_position];
            const time_pos = center_position / sample_rate;
            info_div.text = `<b>Current Correlation:</b> ${cc_val.toFixed(4)} | <b>Time:</b> ${time_pos.toFixed(3)} s`;
        }
    """)
    
    slider.js_on_change('value', callback)
    
    
    # Create layout
    layout = column(p1, p2, slider, info_div, sizing_mode="fixed", width=1200, height=600)
    
    # Output to HTML file
    output_file(output_filename)
    save(layout)
    
    print(f"Standalone HTML file saved as: {output_filename}")
    
    return layout


def normalise(arr):

    return arr / np.max(np.abs(arr))


if __name__ == "__main__":
    
    # Load data
    with h5py.File('../../selected_events.h5', 'r') as fin:

        waveforms = fin.get('waveforms')[:]
        event_types = fin.get('type')[:]
        p_start = fin.get('p_start')[:]
        s_start = fin.get('s_start')[:]

    sample_rate = 100  # Hz

    # -------------------------------------------------------------------------
    # Animation 1:
    # Signal with matching template

    main_signal = normalise(waveforms[0, :, 2])
    time = np.linspace(0, 60, len(main_signal))
    template = main_signal[p_start[0] - 100: s_start[0] + 1000]
    
    # Create the standalone HTML file
    create_standalone_html(
        main_signal, 
        [template], 
        time, 
        sample_rate,
        output_filename="crosscorr_animation_1.html"
    )
    
    # -------------------------------------------------------------------------
    # Animation 2:
    # Signal with mismatching template

    main_signal = normalise(waveforms[2, :, 2])
    #time = np.linspace(0, 60, len(main_signal))
    #template = main_signal[p_start[0] - 100: s_start[0] + 1000]
    
    # Create the standalone HTML file
    create_standalone_html(
        main_signal, 
        [template], 
        time, 
        sample_rate,
        output_filename="crosscorr_animation_2.html"
    )
    
    # -------------------------------------------------------------------------
    # Animation 3:
    # Signal with mismatching but short template

    #main_signal = waveforms[1, :, 2]
    #time = np.linspace(0, 60, len(main_signal))
    #template = main_signal[p_start[0] - 100: s_start[0] + 1000]
    template = template[20:120]
    # 20-120
    
    # Create the standalone HTML file
    create_standalone_html(
        main_signal, 
        [template], 
        time, 
        sample_rate,
        output_filename="crosscorr_animation_3.html"
    )


    # Animation 4: Sum of multiple templates
    templates = []
    i = 2
    while len(templates) < 3:

        print(i, 'event_type:', event_types[i])

        if event_types[i] == 1:
            templ = normalise(waveforms[i, :, 2])
            templ = templ[p_start[i] - 80: p_start[i] + 20]
            templates.append(templ)

        i += 1
        
    create_standalone_html(
            main_signal, 
            templates, 
            time, 
            sample_rate,
            output_filename="crosscorr_animation_4.html"
        )
    
