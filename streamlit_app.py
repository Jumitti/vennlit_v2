from io import BytesIO
from itertools import combinations
from zipfile import ZipFile

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from venn import venn, pseudovenn


@st.cache_data
def download_venn_data(lists):
    items_occurrence = {per_list: set(df[per_list].dropna()) for per_list in lists}
    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, 'a') as zip_file:
        for current_list, items_current_list in items_occurrence.items():
            file_content = "\n".join(items_current_list)
            zip_file.writestr(f"1_{current_list}.txt", file_content)

        for combination_size in range(2, len(lists) + 1):
            for lists_combination in combinations(lists, combination_size):
                shared_items = set.intersection(*(items_occurrence[item] for item in lists_combination))
                items_exclusive_to_combination = shared_items.copy()

                for other_list, items_other_list in items_occurrence.items():
                    if other_list not in lists_combination:
                        items_exclusive_to_combination -= items_other_list

                file_content = "\n".join(items_exclusive_to_combination)
                file_name = f"{len(lists_combination)}_{'_'.join(sorted(lists_combination))}.txt"
                zip_file.writestr(file_name, file_content)

    venn_data = zip_buffer.getvalue()
    return venn_data


def download_png():
    buffer_png = BytesIO()
    plt.savefig(buffer_png, format="png", bbox_inches='tight')
    buffer_png.seek(0)

    return buffer_png


def download_svg():
    buffer_svg = BytesIO()
    plt.savefig(buffer_svg, format="svg", bbox_inches='tight')
    buffer_svg.seek(0)

    return buffer_svg


st.set_page_config(
    page_title="VennLit V2",
    page_icon="⭕",
    layout="wide")

# Diagramme de Venn
st.title('⭕ VennLit V2')

df = []
selection_lists = []

col1, col2, col3 = st.columns([0.8, 1.4, 0.8])

with col1:
    st.subheader("📎 Example and Hints")
    st.link_button("Help", 'https://jumitti.notion.site/jumitti/VennLit-V2-e20a373a9c6f4c1390e72a7953ffcb0c')
    if st.checkbox("**Try example**", value=1):
        with col2:
            st.subheader('Welcome to VennLit V2 😊')
            st.write('You are by default in **demo** mode.\n'
                     'You can play with VennLit V2 or disable **Try example** on the left **📎 Example** section.\n'
                     'You can also click on **Help**.')
        csv_file = 'example/example.csv'
        df = pd.read_csv(csv_file, delimiter=';')
    st.write("**.csv and .xlsx templates:**")
    with open("example/example.csv", "rb") as file:
        st.download_button(
            label="Download example.csv",
            data=file,
            file_name="example.csv",
            mime="text/csv")
    with open("example/example.xlsx", "rb") as file:
        st.download_button(
            label="Download example.xlsx",
            data=file,
            file_name="example.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader("💽 Upload data")
    uploaded_files = st.file_uploader("**Upload one or more .xlsx .csv (delimiter ';') files**", type=["csv", "xlsx"],
                                      accept_multiple_files=True)
    if uploaded_files is not None:
        if len(uploaded_files) > 0:
            dfs = []
            for file in uploaded_files:
                if file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    df = pd.read_excel(file)
                else:
                    df = pd.read_csv(file, delimiter=';')

                dfs.append(df)

            all_columns = [col for df in dfs for col in df.columns]
            duplicate_columns = [col for col in set(all_columns) if all_columns.count(col) > 1]
            if duplicate_columns:
                st.warning(f"Some lists have the same name: {', '.join(duplicate_columns)}")
                filtered_dfs = []
                included_columns = set()
                for df in dfs:
                    filtered_columns = [col for col in df.columns if col not in duplicate_columns]
                    included_columns.update(filtered_columns)
                    filtered_df = df[filtered_columns]
                    filtered_dfs.append(filtered_df)
                df = pd.concat(filtered_dfs, axis=1)

            else:
                df = pd.concat(dfs, axis=1)

    if len(df) > 0:
        st.subheader("🧮 Lists")
        st.dataframe(df, hide_index=True)
        lists = df.columns.tolist()

        with col3:
            st.subheader('📌 Lists selection')
            items_occurrence = {per_list: set(df[per_list].dropna()) for per_list in lists}
            selection_lists = st.multiselect('Lists selection', lists, default=lists[:2], max_selections=6,
                                             placeholder="Choose 2-6 lists", disabled=False,
                                             label_visibility='collapsed')

plt.figure(figsize=(8, 8))

# Setting of configurations

fmt_options = {"Number": "{size}",
               "Percentage": "{percentage:.1f}%",
               "Logic": "{logic}"}

cmap_options = {'Accent': 'Accent',
                'BRG': 'brg',
                "Civids": 'cividis',
                'CMRmap': 'CMRmap',
                "CoolWarm": "coolwarm",
                'CubeHelix': 'cubehelix',
                'Dark2': 'Dark2',
                "Default": 'hsv',
                'Flag': 'flag',
                'Gist Earth': 'gist_earth',
                'Gist Ncar': 'gist_ncar',
                'Gist Rainbow': 'gist_rainbow',
                'Gist Stern': 'gist_stern',
                'GnuPlot': 'gnuplot',
                'GnuPlot2': 'gnuplot2',
                "Inferno": 'inferno',
                'Jet': 'jet',
                "Magma": 'magma',
                'Nipy Spectral': 'nipy_spectral',
                'Ocean': 'ocean',
                'Pastel2': 'Pastel2',
                'Paired': 'Paired',
                "Plasma": 'plasma',
                'Prism': 'prism',
                'Rainbow': 'rainbow',
                'Set1': 'Set1',
                'Set2': 'Set2',
                'Set3': 'Set3',
                "Spectral": "Spectral",
                'Tab10': 'tab10',
                'Tab20': 'tab20',
                'Tab20b': 'tab20b',
                'Tab20c': 'tab20c',
                'Terrain': 'terrain',
                'Turbo': 'turbo',
                "Twilight": 'twilight',
                "Twilight Shifted": 'twilight_shifted',
                "Viridis": 'viridis',
                }

legend_loc_options = {'Best': 'best',
                      'Upper Right': 'upper right',
                      'Upper Left': 'upper left',
                      'Upper Center': 'upper center',
                      'Lower Right': 'lower right',
                      'Lower Left': 'lower left',
                      'Lower Center': 'lower center',
                      'Right': 'right',
                      'Center Right': 'center right',
                      'Center Left': 'center left',
                      'Center': 'center'}

if 1 < len(selection_lists) <= 6:
    num_sets = len(selection_lists)
    selected_lists = selection_lists[:num_sets]

    with col3:
        venn_data = download_venn_data(selected_lists)
        st.download_button(label="💾 Download Venn data",
                           data=venn_data,
                           file_name=f'venn_data{"".join("_" + selected_list for selected_list in selection_lists)}.zip',
                           mime="application/zip", )
        st.divider()
        st.subheader('⚙️Venn diagram settings')
        fmt = st.radio(
            "**Number format:**",
            list(fmt_options.keys()),
            index=0,
            horizontal=True, key='venn_fmt')
        venn_format = fmt_options[fmt]

        cmap = st.selectbox(
            "**Colors:**",
            list(cmap_options.keys()),
            index=7, key='venn_cmap')
        cmap_format = cmap_options[cmap]

        font_size = st.slider("**Font size:**", min_value=5, max_value=20, value=10, step=1, key='venn_font_size',
                              help=None)

        fig_size = st.slider("**Venn size**:", min_value=5, max_value=20, value=10, step=1, key='venn_fig_size',
                             help=None)

        legend_loc = st.selectbox(
            "**Legend position:**",
            list(legend_loc_options.keys()),
            index=0, key='venn_legend_loc')
        legend_loc_format = legend_loc_options[legend_loc]

    with col2:
        st.subheader('Venn diagram')
        dataset_dict = {name: set(items_occurrence[name]) for name in selected_lists}
        venn(dataset_dict, fmt=venn_format, cmap=cmap_format, fontsize=font_size, legend_loc=legend_loc_format,
             figsize=(fig_size, fig_size))
        st.pyplot(plt)

    with col3:
        buffer_png = download_png()
        st.download_button(
            label="Download Venn diagram (.png)",
            data=buffer_png,
            file_name=f'venn{"".join("_" + selected_list for selected_list in selection_lists)}.png',
            mime='image/png',
        )

        buffer_svg = download_svg()
        st.download_button(
            label="Download Venn diagram (.svg)",
            data=buffer_svg,
            file_name=f'venn{"".join("_" + selected_list for selected_list in selection_lists)}.svg',
            mime='image/svg+xml',
        )
        st.write(
            'Try opening the .svg diagram using [Inkscape](https://inkscape.org/) to move shapes, resize, change font, colors and more.')

if len(selection_lists) == 6:
    with col3:
        st.divider()
        st.subheader('⚙️Pseudo-Venn diagram settings',
                     help='Six-set true Venn diagrams are somewhat unwieldy, and not all intersections are usually of interest.\n\n'
                          'If you wish to display information about elements in hidden intersections,'
                          'uncheck the option **hidden intersections** below.\n\n'
                          'Some intersections are not present, but the most commonly wanted are.')
        fmt = st.radio(
            "**Number format:**",
            list(fmt_options.keys()),
            index=0,
            horizontal=True, key='pseudovenn_fmt')
        venn_format = fmt_options[fmt]

        cmap = st.selectbox(
            "**Colors:**",
            list(cmap_options.keys()),
            index=7, key='pseudovenn_cmap')
        cmap_format = cmap_options[cmap]

        font_size = st.slider("**Font size:**", min_value=5, max_value=20, value=10, step=1, key='pseudovenn_font_size',
                              help=None)

        fig_size = st.slider("**Pseudo-Venn size:**", min_value=5, max_value=20, value=10, step=1,
                             key='pseudovenn_fig_size',
                             help=None)

        legend_loc = st.selectbox(
            "**Legend position:**",
            list(legend_loc_options.keys()),
            index=0, key='pseudovenn_legend_loc')
        legend_loc_format = legend_loc_options[legend_loc]

        hint_hidden_format = st.checkbox('**Hidden intersections**', value=1,
                                         help='Six-set true Venn diagrams are somewhat unwieldy, and not all intersections are usually of interest.\n\n'
                                              'If you wish to display information about elements in hidden intersections,'
                                              'uncheck the option **hidden intersections**.\n\n'
                                              'Some intersections are not present, but the most commonly wanted are.')

    with col2:
        st.subheader('Pseudo-Venn diagram')
        dataset_dict = {
            name: set(items_occurrence[selection_lists[i]]) for i, (name, items) in enumerate(items_occurrence.items())}
        pseudovenn(dataset_dict, fmt=venn_format, cmap=cmap_format, fontsize=font_size, legend_loc=legend_loc_format,
                   figsize=(fig_size, fig_size),
                   hint_hidden=False if hint_hidden_format else True)
        st.pyplot(plt)

    with col3:
        buffer_png = download_png()
        st.download_button(
            label="Download Pseudo-Venn diagram (.png)",
            data=buffer_png,
            file_name=f'pseudovenn{"".join("_" + selected_list for selected_list in selection_lists)}.png',
            mime='image/png',
        )

        buffer_svg = download_svg()
        st.download_button(
            label="Download Pseudo-Venn diagram (.svg)",
            data=buffer_svg,
            file_name=f'pseudovenn{"".join("_" + selected_list for selected_list in selection_lists)}.svg',
            mime='image/svg+xml',
        )
        st.write(
            'Try opening the .svg diagram using [Inkscape](https://inkscape.org/) to move shapes, resize, change font, colors and more.')
