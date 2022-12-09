import mbe_get_steps, tdms_converter, tdms_extraction


def main():
    mbe_get_steps.get_mbe_steps_main()
    tdms_converter.convert_tdms_files()
    tdms_extraction.tdms_extraction_main()

if __name__ == '__main__':
    main()

