import subprocess


def run_command(command):
    """
    Execute a command as a subprocess and print the output.
    This function is used to run PLINK and SHAPEIT commands from within Python.

    :param command: Command to be executed (in list format).
    """

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Command executed: {' '.join(command)}\nOutput: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}\nError: {e.stderr}")


def remove_duplicate_ids(fam_file):
    """
    Removes duplicate individual IDs from a PLINK .fam file.

    :param fam_file: Path to the .fam file to be processed.
    """

    with open(fam_file, 'r') as file:
        lines = file.readlines()
        seen = set()
        unique_lines = []
        for line in lines:
            _, iid = line.strip().split()[:2]
            if iid not in seen:
                seen.add(iid)
                unique_lines.append(line)

    with open(fam_file, 'w') as file:
        file.writelines(unique_lines)
    print(f"Removed duplicates from {fam_file}")


def plink_data_processing(file_prefix, name_file_path=None):
    """
    Process data using PLINK wirh chromosome separation.

    :param file_prefix: Prefix for output files.
    :param name_file_path: Path to the file containing individuals to be removed (optional).
    """

    fam_file = f"{file_prefix}_binary.fam"

    # Converting to binary format for more efficient processing
    run_command(["/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink", "--file", file_prefix, "--make-bed", "--out", f"{file_prefix}_binary"])
    remove_duplicate_ids(fam_file)

    # Processing steps using plink
    commands = [
        ["/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink", "--bfile", f"{file_prefix}_binary", "--geno", "0.05", "--make-bed", "--out", f"{file_prefix}_snp_callrate_filtered"],
        ["/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink", "--bfile", f"{file_prefix}_snp_callrate_filtered", "--mind", "0.1", "--make-bed", "--out", f"{file_prefix}_indiv_callrate_filtered"],
        ["/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink", "--bfile", f"{file_prefix}_indiv_callrate_filtered", "--maf", "0.01", "--make-bed", "--out", f"{file_prefix}_maf_filtered"],
        ["/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink", "--bfile", f"{file_prefix}_maf_filtered", "--hwe", "1e-6", "--make-bed", "--out", f"{file_prefix}_hwe_filtered"],
        ["/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink", "--bfile", f"{file_prefix}_hwe_filtered", "--chr", "1-22", "--make-bed", "--out", f"{file_prefix}_autosomes"],
    ]

    for command in commands:
        run_command(command)

    # Removing specific individuals and dividing by chromosomes
    final_command = ["/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink", "--bfile", f"{file_prefix}_autosomes", "--make-bed", "--out", f"{file_prefix}_filtered"]
    if name_file_path:
        final_command.insert(2, "--remove")
        final_command.insert(3, name_file_path)

    run_command(final_command)

    for chr_num in range(1, 23):
        # Generate BED file
        run_command([
            "/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink",
            "--bfile", f"{file_prefix}_filtered",
            "--chr", str(chr_num),
            "--make-bed", "--out", f"{file_prefix}_filtered_chr{chr_num}"
        ])

        # Generate VCF file
        run_command([
            "/Users/kristinagrigaityte/PycharmProjects/ArchIE/plink/plink",
            "--bfile", f"{file_prefix}_filtered_chr{chr_num}",
            "--recode", "vcf",
            "--out", f"{file_prefix}_filtered_chr{chr_num}"
        ])


plink_data_processing("Lithuanian_raw_SNP_final", name_file_path="/Users/kristinagrigaityte/PycharmProjects/ArchIE/data/people.txt")
