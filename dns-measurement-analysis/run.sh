#!/bin/bash

echo "Filter for necessary fields in pcap scan data..."
# Usage: ./parse_and_sanitize_scan_io_data.sh $pcap_directory$ $directory_for_output_csv_files$
./parse_and_sanitize_scan_io_data.sh ./raw_pcap_scan_data ./sanitized_csv_scan_data

# Usage: python3 match_scan_requests_and_responses.py $csv_directory_of_previous_step$ $IP_address_of_scanning_interface$
echo "Matching outgoing responses with incoming requests..."
python3 match_scan_requests_and_responses.py ./sanitized_csv_scan_data 141.22.28.227

# Usage: python3 Postprocessing_Dataframe.py $csv_directory_of_previous_step$ $asndb_file$
echo "Concating dataframes and mapping AS numbers and country codes..."
python3 Postprocessing_Dataframe.py ./sanitized_csv_scan_data/ ./pyasn_db/IPASN/ipasn-2021-09-20.gz

echo "Starting analysis script..."
python3 Paper_Plots.py ./dataframes/dataframe_for_analysis.csv.gz

echo "Created Plots. Go to ./figures/ to see plots."

echo "End of Script."
