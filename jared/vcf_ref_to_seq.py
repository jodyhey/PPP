import Bio
import sys
import pysam
import argparse
from gene_region import Region, RegionList




#Input: VCF file, reference sequence, region list (possibly .bed file)
#Output: Sequences with reference genome overlayed with VCF SNP calls

def checkRecordIsSnp(rec):
    """Checks if this record is a single nucleotide variant, returns bool."""
    if len(rec.ref) != 1:
        return False
    for allele in rec.alts:
        if len(allele) != 1:
            return False
    return True

	
def indivIdx(indiv):
    """For now, returns individual haplotype as an individual index and 
    individual haplotype index. May be expanded for non-diploid samples"""
    return indiv/2,indiv%2

def generateSequence(vcf_reader,ref_seq,region,chrom,indiv):
    """Fetches variant sites from a given region, then outputs sequences
    from each individual with their correct variants. Will print sequence
    up to the variant site, then print correct variant. After last site,
    will output the rest of the reference sequence."""
    var_sites = vcf_reader.fetch(chrom,region.start,region.end)
    fl = 0
    seq = ''
    prev_offset = 0

    while fl == 0:
        try:
            vcf_record = next(var_sites)
        except:
            fl = 1
            break

        if not checkRecordIsSnp(vcf_record):
            continue

        pos_offset = vcf_record.pos - 1 - region.start
        for i in xrange(prev_offset,pos_offset-1):
            seq += ref_seq[i]

        idv,idx = indivIdx(indiv)
        seq += vcf_record.samples[idv].alleles[idx]
        prev_offset = pos_offset

    for i in xrange(prev_offset,len(ref_seq)):
        seq += ref_seq[i]

    return seq
        


parser = argparse.ArgumentParser(description=("Generates sequences from samples"
                                 "from a VCF file, a reference genome, and a"
                                 "list of gene regions."))
parser.add_argument("--vcf", dest="vcfname",help="Input VCF filename")
parser.add_argument("--ref",dest="refname",help="Reference FASTA file")
parser.add_argument("--gr",dest="genename",help="Name of gene region file")
parser.add_argument("-g1",dest="gene_idx",action="store_true",help="Gene Region list is 1 index based, not 0")

args = parser.parse_args()

region_list = RegionList(args.genename)

vcf_reader = pysam.VariantFile(args.vcfname)
first_el = next(vcf_reader)
chrom = first_el.chrom
sample_size = len(first_el.samples)*2

fasta_ref = pysam.FastaFile(args.refname)

for region in region_list.regions:
    ref_seq = fasta_ref.fetch(chrom,region.start,region.end)
    print ">TestHeader"
    for i in xrange(sample_size):
        seq = generateSequence(vcf_reader,ref_seq,region,chrom,i)
        print seq

