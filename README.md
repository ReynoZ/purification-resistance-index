# purification-resistance-index
 
Codes and demos for PRI calculation.

## Introduction to PRI

Water quality assessment plays a significant role in ensuring the availability of clean and safe water. The Water Quality Index (WQI) model method has been developed to provide a basis for assessing water quality by integrating various water quality parameters. However, existing WQIs do not “actively” consider the difficulty of water treatment from raw water to specific water use scenarios. This study proposes a novel model framework, named as Purification Resistance Index (PRI), quantitatively evaluating not only the exceedance of pollutants but also how difficult they can be removed in the water treatment process. The framework is built based on the conventional drinking water treatment processes, with sub-indices for coagulation-sedimentation ($r_c$), filtration ($r_f$), disinfection ($r_d$), and advanced treatment ($r_a$). The model considers appropriate weights assigned to each sub-index to calculate the purification resistance, resulting in a comprehensive index for water quality evaluation. Case studies on nationwide and citywide water source reservoirs demonstrated the applicability of PRI approach.  PRI breakthrough the traditional water quality risk assessment paradigm and extents to engineering region and provide useful auxiliary information for water source management, drinking water treatment plant planning and updating, operation control, and other purposes. It is open for more practices validation and discussion.

## Content of this Repository

This Repository contains the main programme to calculate PRI for a given set of water quality observation data, as well as the references it needs when doing the calculation.

- `main_programme.py` is the main programme. This programme will automatically read in the input file in the folder `Input` and calculate the four sub-indices of PRI. The output file will be generated in the folder `Output`.
- `calc_subindex.py` contains essential functions needed to calculate the four sub-indices. There is no need to modify it, unless you wish to adjust the model structure to fit your data availability.
- `Input` is where you put the input files.
- `Output` is where the evaluation result will be generated.
- `ref_data` contains limit values used for each sub-index. You are free to adjust the limit values to comply with the local laws.

## How to use?

1. Put your Input file in the `Input` folder.
2. Run `main_programme.py`. (The default code reads in a demo file in the input folder)
3. Check the result file generated in folder `Output`.

Notice: The data input for PRI calculation should be formatted as the `demo.csv` file. You can also adjust the code to adapt your unique data format. Make sure the parameters are identical with the demo. If you want to include extra water parameters or change the exsisting ones, please refer to the code in `calc_subindex.py` and modify accordingly. The baseline values used are stored in csv files in the folder `ref_data`. You are free to examine those and modify according to your local regulations.