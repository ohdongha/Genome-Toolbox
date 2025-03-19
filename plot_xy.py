#!/usr/bin/env python

import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def plot_xy(file, x_col, y_col, output_file, 
            z_col=None, x_err_col=None, y_err_col=None, 
            plot_size=None, x_range=None, y_range=None, x_label=None, y_label=None, 
            x_tick=0, x_in_K=False, y_tick=0, y_in_K=False,
            title=None, alpha=1.0, marker_size=0, palette=None, use_marker_style=False, svg=False, 
            separate_legends=False, separate_legends_h=False, legend_col=4,
            font='Arial', font_size=10):
    # Load data
    df = pd.read_csv(file, delimiter='\t')
    
    # Convert column indices (starting from 1) to zero-based index
    try:
        x_col = int(x_col) - 1 if x_col.isdigit() else x_col
        y_col = int(y_col) - 1 if y_col.isdigit() else y_col
        z_col = int(z_col) - 1 if z_col and z_col.isdigit() else z_col
        x_err_col = int(x_err_col) - 1 if x_err_col and x_err_col.isdigit() else x_err_col
        y_err_col = int(y_err_col) - 1 if y_err_col and y_err_col.isdigit() else y_err_col
    except ValueError:
        print("Error: Column indices should be numeric or valid column names.")
        return
    
    # If using indices, map them to actual column names
    if isinstance(x_col, int):
        x_col = df.columns[x_col]
    if isinstance(y_col, int):
        y_col = df.columns[y_col]
    if isinstance(z_col, int):
        z_col = df.columns[z_col]
    if isinstance(x_err_col, int):
        x_err_col = df.columns[x_err_col]
    if isinstance(y_err_col, int):
        y_err_col = df.columns[y_err_col]
    
    # Check if provided columns exist
    if x_col not in df.columns or y_col not in df.columns:
        print(f"Error: Columns {x_col} and/or {y_col} not found in file.")
        return
    if z_col and z_col not in df.columns:
        print(f"Warning: Column {z_col} not found, proceeding without color encoding.")
        z_col = None
    if x_err_col and x_err_col not in df.columns:
        print(f"Warning: Column {x_err_col} not found, proceeding without x error bars.")
        x_err_col = None
    if y_err_col and y_err_col not in df.columns:
        print(f"Warning: Column {y_err_col} not found, proceeding without y error bars.")
        y_err_col = None

    # Set the plot size (in inches)
    try:
        figsize = tuple(map(float, plot_size.split(',')))
        if len(figsize) != 2:
            raise ValueError
    except ValueError:
        print("Invalid plot_size format. Using default size (10, 6).")
        figsize = (10, 6)
    plt.figure(figsize=figsize)    

    # Set font and font scale
    plt.rcParams.update({
        "font.family": font,
        "font.size": font_size,  # Base font size (scales everything proportionally)
    })

    # Create scatter plot
    if use_marker_style:
        if marker_size >= 40:
            scatter = sns.scatterplot(data=df, x=x_col, y=y_col, hue=z_col, s=marker_size, style=z_col, palette=palette, edgecolor='black', alpha=alpha)
        else:
            scatter = sns.scatterplot(data=df, x=x_col, y=y_col, hue=z_col, style=z_col, palette=palette, edgecolor='black', alpha=alpha)
    else:
        scatter = sns.scatterplot(data=df, x=x_col, y=y_col, hue=z_col, palette=palette, edgecolor='black', alpha=alpha)
    
    # Capture legend handles and labels before removing legend from main plot
    handles, labels = scatter.get_legend_handles_labels() if z_col else ([], [])
    if separate_legends or separate_legends_h:
        scatter.legend_.remove()
    
    # Set axis labels
    plt.xlabel(x_label if x_label else x_col)
    plt.ylabel(y_label if y_label else y_col)
    
    # Set axis ranges
    if x_range:
        plt.xlim(tuple(map(float, x_range.split(','))))
    if y_range:
        plt.ylim(tuple(map(float, y_range.split(','))))

    # If needed, set x- and y-axis tick interval
    if x_tick != 0:
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(x_tick))
    if y_tick != 0:
        plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(y_tick))

    # If x- and/or y-axis needs to be in thousands (K)
    def thousands_formatter(x, pos):
        if x == 0:
            return '0'
        elif x % 1000 == 0:
            return f'{int(x / 1000)}K'
        else:
            return f'{x / 1000:.1f}K'
    if x_in_K:
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(thousands_formatter))
    if y_in_K:
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(thousands_formatter))

    # If asked, add error bars
    if x_err_col or y_err_col:
        plt.errorbar(
            df[x_col], df[y_col], 
            xerr=df[x_err_col] if x_err_col else None, 
            yerr=df[y_err_col] if y_err_col else None, 
            fmt='none', ecolor='gray', elinewidth=1, alpha=0.8
        )

    # Set title
    if title is None:
        plt.title(f"Scatter Plot of {y_col} vs {x_col}")
    elif title:
        plt.title(title)
    
    # Save plot to file
    if svg:
        output_file = output_file.rsplit('.', 1)[0] + ".svg"
    plt.savefig(output_file, bbox_inches='tight')
    print(f"Plot saved as {output_file}")
    
    # Save separate legend if requested
    if separate_legends and z_col:
        legend_fig, legend_ax = plt.subplots(figsize=(3, 6))
        if marker_size >= 40:
            legend_ax.legend(handles, labels, title=z_col, loc='center', ncol=num_columns, frameon=False, markerscale=marker_size/40)
        else:
            legend_ax.legend(handles, labels, title=z_col, loc='center', ncol=num_columns, frameon=False)
        legend_ax.axis('off')
        legend_output = output_file.rsplit('.', 1)[0] + ("_legends.svg" if svg else "_legends.png")
        legend_fig.savefig(legend_output, bbox_inches='tight')
        print(f"Legend saved as {legend_output}")
    
    # Save separate legend printing them horizontally 
    if separate_legends_h and z_col:
        items_per_row = legend_col
        num_columns = min(items_per_row, len(labels))
        legend_fig, legend_ax = plt.subplots(figsize=(num_columns * 2, 1))  # Adjust width as needed
        if marker_size >= 40:
            legend_ax.legend(handles, labels, title=z_col, loc='center', ncol=num_columns, frameon=False, markerscale=marker_size/40)
        else:
            legend_ax.legend(handles, labels, title=z_col, loc='center', ncol=num_columns, frameon=False)
        legend_ax.axis('off')
        legend_output = output_file.rsplit('.', 1)[0] + ("_legends.svg" if svg else "_legends.png")
        legend_fig.savefig(legend_output, bbox_inches='tight')
        print(f"Legend saved as {legend_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot X-Y scatter plot with optional color hue.")
    parser.add_argument("file", nargs='?', help="Path to tab-delimited file")
    parser.add_argument("x_col", nargs='?', help="Column index (1-based) or name for X-axis")
    parser.add_argument("y_col", nargs='?', help="Column index (1-based) or name for Y-axis")
    parser.add_argument("output_file", nargs='?', help="Output file name (e.g., output.png)")
    parser.add_argument("--z_col", help="(Optional) Column index (1-based) or name for color hue", default=None)
    parser.add_argument("--x_err_col", help="(Optional) Column index (1-based) or name for x error bars", default=None)
    parser.add_argument("--y_err_col", help="(Optional) Column index (1-based) or name for y error bars", default=None)
    parser.add_argument("--plot_size", help="(Optional) plot size as horizontal,vertial in inches [10.0,6.0]", default="10.0,6.0")
    parser.add_argument("--x_range", help="(Optional) X-axis range as min,max", default=None)
    parser.add_argument("--y_range", help="(Optional) Y-axis range as min,max", default=None)
    parser.add_argument("--x_tick", help="(Optional) X-axis tick interval to use, e.g., 2000", type=float, default=0)
    parser.add_argument("--x_in_K", help="(Optional) X-axis showin in thousand (K) unit", action="store_true")
    parser.add_argument("--y_tick", help="(Optional) Y-axis tick interval to use, e.g., 2000", type=float, default=0)
    parser.add_argument("--y_in_K", help="(Optional) Y-axis showin in thousand (K) unit", action="store_true")
    parser.add_argument("--x_label", help="(Optional) Label for X-axis", default=None)
    parser.add_argument("--y_label", help="(Optional) Label for Y-axis", default=None)
    parser.add_argument("--title", help="(Optional) Title for the plot, use empty string to disable", default=None)
    parser.add_argument("--alpha", help="(Optional) Transparency level for points (0 to 1)", type=float, default=1.0)
    parser.add_argument("--marker_size", help="(Optional) Size of data points; minimum 40", type=int, default=0)
    parser.add_argument("--pallette", help="(Optional) Seaborn pallette to use when 'z_col' is given", type=str, default="viridis")
    parser.add_argument("--use_marker_style", help="(Optional) Use also Seaborn marker styles when 'z_col' is given", action="store_true")
    parser.add_argument("--svg", help="(Optional) Save plot as SVG instead of PNG", action="store_true")
    parser.add_argument("--separate_legends", help="(Optional) Save legends separately in a different file", action="store_true")
    parser.add_argument("--separate_legends_h", help="(Optional) Save legends in multiple (N) columns in a different file", action="store_true")
    parser.add_argument("--legend_col", help="(Optional) Set the N when '--separate_legends_h' is on, by default 4", type=int, default=4)
    parser.add_argument("--font", help="(Optional) Matplotlib font family to use instead of 'Arial'", type=str, default="Arial")
    parser.add_argument("--font_size", help="(Optional) Matplotlib base font size to use instead of the default 10", type=int, default=10)
    
    args = parser.parse_args()
    
    if not args.file or not args.x_col or not args.y_col or not args.output_file:
        parser.print_usage()
    else:
        plot_xy(args.file, args.x_col, args.y_col, args.output_file, 
                args.z_col,args.x_err_col,args.y_err_col,
                args.plot_size,args.x_range, args.y_range, args.x_label, args.y_label, 
                args.x_tick, args.x_in_K, args.y_tick, args.y_in_K,
                args.title, args.alpha, args.marker_size, args.pallette, args.use_marker_style, args.svg, 
                args.separate_legends, args.separate_legends_h, args.legend_col,
                args.font, args.font_size)

