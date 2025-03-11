
class PalletTableGenerator:
    def __init__(self):
        self.column_widths = {
            'NR': 9,
            'TYPE': 8,
            'NAME': 61,
            'DATUM': 31,
            'PRESET': 8,
            'LOCATION': 9,
            'LOCK': 5,
            'W-STATUS': 12,
            'METHOD': 7,
            'CTID': 8
        }
        
    def format_line(self, data_dict):
        """Format a single line according to the fixed width specification"""
        line = ''
        for col, width in self.column_widths.items():
            value = str(data_dict.get(col, ''))
            line += value.ljust(width)
        return line.rstrip() + '\n'  # Remove trailing spaces but add newline
    
    def get_preset(self, quadrant):
        if quadrant == "A":
            return 31
        elif quadrant == "B":
            return 32
        elif quadrant == "C":
            return 33
        elif quadrant == "D":
            return 34
        else:
            raise ValueError(f"Invalid quadrant number: {quadrant}")
        
    def generate_pallet_table(self, operations_df, output_path, filename):

        # PREPARE OPERATIONS DATAFRAME
        planned_ops = operations_df[operations_df['status'] == 'planned'].copy()
        if planned_ops.empty:
            raise ValueError("No planned operations found in the operations DataFrame")
        planned_ops = planned_ops.sort_values(['pallet', 'quadrant'])
        
        # INITIATE PALLET TABLE
        content = ["BEGIN " + filename+' MM\n']
        header_dict = {col: col for col in self.column_widths.keys()}
        content.append(self.format_line(header_dict))
        
        # ADD PALLET ENTRIES
        current_pallet = None
        line_number = 0
        
        #check if pallet change is necessary (if yes add pallet change, if no add opperations at correct preset)
        for i, row in planned_ops.iterrows():
            pallet = row['pallet']
            quadrant = row['quadrant']
            preset = self.get_preset(quadrant)
            file_name = row['hfile']
            
            # CHANGE PALLET LINE
            if pallet != current_pallet:    
                change_pallet_dict = {
                    'NR': str(line_number),
                    'TYPE': 'PAL',
                    'NAME': str(int(pallet)),
                    'DATUM': "",
                    'PRESET': '',
                    'LOCATION': 'MA',
                    'LOCK': '',
                    'W-STATUS': '',
                    'METHOD': '',
                    'CTID': ''
                    }
                current_pallet = pallet
                line_number += 1
                content.append(self.format_line(change_pallet_dict))
            
            #OPERATION-PRESET LINE
            operation_dict = {
                'NR': str(line_number),
                'TYPE': 'PGM',
                'NAME': str(file_name),
                'DATUM': "DATUM_ARRAY_Z.D",
                'PRESET': str(preset),
                'LOCATION': '',
                'LOCK': '',
                'W-STATUS': "",
                'METHOD': 'WPO',
                'CTID': ''
                }
            line_number += 1
            content.append(self.format_line(operation_dict))

        # Add footer
        content.append('[END]\n')
        
        # Write to file
        with open(output_path, 'w') as f:
            f.writelines(content)
        
        return True

