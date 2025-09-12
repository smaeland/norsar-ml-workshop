import numpy as np
from bokeh.layouts import column, row, layout
from bokeh.models import ColumnDataSource, CustomJS, Slider, Button
from bokeh.plotting import figure, show, output_file, save

import matplotlib.pyplot as plt

DEBUG = False

marker_size = 16
line_width = 5

def generate_data(num, seed):

    rng = np.random.default_rng(seed=seed)
    x = rng.uniform(size=num)
    y = np.sin(2*np.pi*x) + rng.normal(scale=0.1, size=num)

    return x, y


X_train, y_train = generate_data(20, 42)
X_test, y_test = generate_data(50, 1)

x_min, x_max = -0.1, 1.1

def plot_data_only(output_filename):

    output_file(filename=output_filename, title='Plot of data only')

    data = ColumnDataSource(data={'x': X_train, 'y': y_train})

    plot = figure(
        x_range=(x_min, x_max),
        y_range=(-1.5, 1.5),
        sizing_mode='stretch_both',
        tools='pan,wheel_zoom,box_zoom,reset,crosshair',
        active_drag='pan',
        active_scroll='wheel_zoom'
    )
    plot.scatter(x='x', y='y', source=data, size=marker_size)

    if DEBUG:
        show(plot)
    else:
        save(plot)




def plot_hyperparameters(output_filename):

    output_file(filename=output_filename, title='Plot of different hyperparameter values')

    data = ColumnDataSource(data={'x': X_train, 'y': y_train})
    data_test = ColumnDataSource(data={'x': X_test, 'y': y_test})
    model = ColumnDataSource(
        data={
            'x': np.linspace(x_min, x_max, 150),
            'y': np.zeros(shape=(150,))
        }
    )

    order_min, order_max = 0, 20

    # Initialize parameters
    orders = list(range(order_min, order_max+1))

    # Create plot
    plot = figure(
        x_range=(0, 1),
        y_range=(-1.5, 1.5),
        sizing_mode='stretch_both',
        min_width=400,
        tools='pan,wheel_zoom,box_zoom,reset,crosshair',
        active_drag='pan',
        active_scroll='wheel_zoom'
    )
    plot.scatter(x='x', y='y', source=data, size=marker_size, color='royalblue')

    function = plot.line(x='x', y='y', source=model, line_width=line_width, line_alpha=0.6)
    function.visible = False

    circles = plot.scatter('x', 'y', size=marker_size, color='crimson',  source=data_test)
    circles.visible = False

    # Fit parameters for each polynomial order
    params = {}
    for i in orders:
        params_i = np.polyfit(data.data['x'], data.data['y'], deg=i)
        params_i = np.flip(params_i, 0) #  :=
        params_i = np.pad(params_i, (0, len(orders)-i))

        params[f'p{i}'] = np.array(params_i)

        #print('order:', i, 'params:', params_i)

        """
        if DEBUG:
            xvals = model.data['x']
            poly = np.poly1d(params_i)(xvals)
            plt.scatter(data.data['x'], data.data['y'])
            plt.plot(xvals, poly)
            plt.show()
        """

    parameters = ColumnDataSource(
        data=params
    )
    # print('params:')
    # print(params)

    m = Slider(start=order_min, end=order_max, value=0, step=1, title="m")
    slider_callback = CustomJS(args=dict(model=model, params=parameters, deg=m),
        code="""
        const _deg = deg.value;

        const pars = [
            params.data.p0,
            params.data.p1,
            params.data.p2,
            params.data.p3,
            params.data.p4,
            params.data.p5,
            params.data.p6,
            params.data.p7,
            params.data.p8,
            params.data.p9,
            params.data.p10,
            params.data.p11,
            params.data.p12,
            params.data.p13,
            params.data.p14,
            params.data.p15,
            params.data.p16,
            params.data.p17,
            params.data.p18,
            params.data.p19,
            params.data.p20,
        ];

        const par = pars[_deg];
        const x = model.data.x;
        const y = Array.from(x, (x) => par[0]
            + par[1]*x
            + par[2]*Math.pow(x, 2)
            + par[3]*Math.pow(x, 3)
            + par[4]*Math.pow(x, 4)
            + par[5]*Math.pow(x, 5)
            + par[6]*Math.pow(x, 6)
            + par[7]*Math.pow(x, 7)
            + par[8]*Math.pow(x, 8)
            + par[9]*Math.pow(x, 9)
            + par[10]*Math.pow(x, 10)
            + par[11]*Math.pow(x, 11)
            + par[12]*Math.pow(x, 12)
            + par[13]*Math.pow(x, 13)
            + par[14]*Math.pow(x, 14)
            + par[15]*Math.pow(x, 15)
            + par[16]*Math.pow(x, 16)
            + par[17]*Math.pow(x, 17)
            + par[18]*Math.pow(x, 18)
            + par[19]*Math.pow(x, 19)
            + par[20]*Math.pow(x, 20)
        );
        model.data = { x, y };
    """)

    m.js_on_change('value', slider_callback)

    test_data_toggle = Button(label="Show test data", button_type="primary")
    test_data_callback = CustomJS(args=dict(glyph=circles, button=test_data_toggle),
        code="""
        if (glyph.visible) {
            glyph.visible = false;
            button.label = "Show test data";
        } else {
            glyph.visible = true;
            button.label = "Hide test data";
        }
    """)
    test_data_toggle.js_on_click(test_data_callback)

    show_function_toggle = Button(label="Show model", button_type="primary")
    show_function_callback = CustomJS(args=dict(glyph=function, button=show_function_toggle),
        code="""
        if (glyph.visible) {
            glyph.visible = false;
            button.label = "Show model";
        } else {
            glyph.visible = true;
            button.label = "Hide model";
        }
    """)
    show_function_toggle.js_on_click(show_function_callback)


    grid = column([row([m, show_function_toggle, test_data_toggle]), plot], sizing_mode='stretch_both')

    if DEBUG:
        show(grid)
    else:
        save(grid)



#plot_data_only('over_underfitting_data_only.html')
plot_hyperparameters('over_underfitting_hyperpars.html')
