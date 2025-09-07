import numpy as np
from obspy.signal.cross_correlation import correlate_template
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, Span, CustomJS, Div
from bokeh.models.tools import PanTool, BoxZoomTool, ResetTool, WheelZoomTool

def create_standalone_html(main_signal, template, time_vector, sample_rate, 
                           output_filename="cross_correlation_app.html"):
    """
    Create a standalone HTML file with Bokeh app for cross-correlation visualization
    
    Parameters:
    -----------
    main_signal : array-like
        The main seismic time series
    template : array-like
        The template waveform to match
    time_vector : array-like
        Time values corresponding to main_signal
    sample_rate : float
        Sampling rate of the signals (Hz)
    output_filename : str
        Name of the output HTML file
    """
    
    # Compute cross-correlation for all possible positions
    #cc_values = cross_correlation(main_signal, template)
    cc_values = correlate_template(main_signal, template, mode='same')
    
    # Create time vector for cross-correlation (shifts)
    max_shift = len(main_signal) - len(template)
    #cc_time = (np.arange(len(cc_values)) - len(template)//2) / sample_rate
    cc_time = np.arange(len(cc_values)) / sample_rate
    
    # Prepare all possible template positions
    # We'll store all positions in the data source and use JavaScript to show/hide
    #template_positions_time = []
    #template_positions_amp = []
    
    #for i in range(max_shift + 1):
    #    if i < len(main_signal) - len(template) + 1:
    #        t_time = time_vector[i:i+len(template)]
    #        template_positions_time.append(t_time.tolist())
    #        template_positions_amp.append(template.tolist())
    
    # Create data sources
    # Main signal source
    main_source = ColumnDataSource(data=dict(
        time=time_vector,
        amplitude=main_signal
    ))
    
    # Template source with all positions stored
    template_source = ColumnDataSource(data=dict(
        time=time_vector[:len(template)],  # Initial position
        times_at_t0=time_vector[:len(template)],
        amplitude=template,
        #all_times=template_positions_time,  # All possible positions
        #all_amplitudes=template_positions_amp,
        #template_length=[len(template)]
    ))
    
    # Cross-correlation source
    cc_source = ColumnDataSource(data=dict(
        time=cc_time,
        correlation=cc_values
    ))
    
    # Create figures
    # Top panel: Main signal and template overlay
    p1 = figure(
        width=800, 
        height=300, 
        title="Seismic Waveform with Template Overlay",
        x_axis_label="Time (s)",
        y_axis_label="Amplitude",
        tools=[PanTool(), BoxZoomTool(), ResetTool(), WheelZoomTool()],
        # active_scroll='wheel_zoom'
    )
    
    # Plot main signal
    p1.line('time', 'amplitude', source=main_source, 
            line_width=1, color='blue', alpha=0.7, legend_label="Main Signal")
    
    # Plot template (will move with slider)
    template_line = p1.line('time', 'amplitude', source=template_source, 
                           line_width=2, color='red', legend_label="Template")
    
    p1.legend.location = "top_right"
    p1.legend.click_policy = "hide"
    
    # Bottom panel: Cross-correlation
    p2 = figure(
        width=800, 
        height=300,
        title="Cross-Correlation",
        x_axis_label="Template Position (s)",
        y_axis_label="Correlation",
        tools=[PanTool(), BoxZoomTool(), ResetTool(), WheelZoomTool()],
        # active_scroll='wheel_zoom',
        x_range=p1.x_range  # Link x-ranges
    )
    
    # Plot cross-correlation
    p2.line('time', 'correlation', source=cc_source, 
            line_width=1, color='green')
    
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
                   width=800, height=30)
    
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
        
        // Update template position on the main signal plot
        //const all_times = template_source.data['all_times'];
        //const all_amplitudes = template_source.data['all_amplitudes'];
        
        //if (position < all_times.length) {
        //    template_source.data['time'] = all_times[position];
        //    template_source.data['amplitude'] = all_amplitudes[position];
        //    template_source.change.emit();
        //}
        const times_at_t0 = template_source.data['times_at_t0']
        //const template_half_length = times_at_t0.length;
        //const center_position = position - Math.floor(template_half_length / 2);

        const times = times_at_t0.map(item => item + (position / sample_rate));
        template_source.data['time'] = times
        //console.log('time_at_t0:', template_source.data['time_at_t0'])
        //console.log('times:', times)
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
    layout = column(p1, p2, slider, info_div)
    
    # Output to HTML file
    output_file(output_filename)
    save(layout)
    
    print(f"Standalone HTML file saved as: {output_filename}")
    
    return layout

# Example usage
if __name__ == "__main__":
    # Example cross_correlation function (replace with your actual function)
    def cross_correlation(signal, template):
        """
        Compute normalized cross-correlation between signal and template
        """
        from scipy import signal as scipy_signal
        
        # Normalize inputs
        signal_norm = (signal - np.mean(signal)) / np.std(signal)
        template_norm = (template - np.mean(template)) / np.std(template)
        
        # Compute cross-correlation
        correlation = scipy_signal.correlate(signal_norm, template_norm, mode='valid')
        correlation = correlation / len(template)  # Normalize by template length
        
        return correlation
    
    # Generate example data
    sample_rate = 100  # Hz
    duration = 10  # seconds
    time = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create main signal with an embedded pattern
    np.random.seed(42)
    main_signal = np.random.randn(len(time)) * 0.5
    
    # Create template
    template_length = int(sample_rate * 0.5)  # 0.5 second template
    template_time = np.linspace(0, 0.5, template_length)
    template = np.sin(2 * np.pi * 5 * template_time) * np.exp(-template_time * 3)
    
    # Embed template at a few positions in the main signal
    positions = [200, 500, 750]  # Sample positions
    for pos in positions:
        if pos + len(template) < len(main_signal):
            main_signal[pos:pos+len(template)] += template * 2
    
    # Create the standalone HTML file
    create_standalone_html(
        main_signal, 
        template, 
        time, 
        sample_rate,
        output_filename="seismic_correlation_viewer.html"
    )
    
