workflow RtmGermline {
  File ref_fasta
  File ref_fasta_index = ref_fasta + ".fai"
  File ref_dict = ref_fasta + ".dict"
  File ref_alt = sub(ref_fasta, ".fasta$", ".dict")
  File ref_bwt = ref_fasta + ".bwt"
  File ref_sa = ref_fasta + ".sa"
  File ref_amb = ref_fasta + ".amb"
  File ref_ann = ref_fasta + ".ann"
  File ref_pac = ref_fasta + ".pac"

  Array[File] bqsr_known_sites
  Array[File] bqsr_known_sites_indexes
  File dbSNP
  File dbSNP_index = dbSNP + ".tbi"
  
  Int threads_bwa
  String mem_bwa
  Int threads_samsort
  String mem_samsort
  Int threads_bqsr
  String mem_bqsr
  Int threads_dedup
  String mem_dedup
  Int threads_hc
  String mem_hc
  Int threads_genotype
  String mem_genotype
  Int threads_hsmet
  String mem_hsmet

  String? java_options
  String gatk_options
  String? HaplotypeCaller_options
  Int mincalldepth

  File intervals
  File probe_intervals

  String dataset
  File fastqfp1
  File fastqfp2
  File fastqfp3
  File fastqfp4
  String RG_ID = dataset
  String RG_SM
  String RG_PL
  String RG_PU
  String RG_LB

  call AlignBwa {
      input:
          out =  dataset,
          fastq1 = fastqfp1,
          fastq2 = fastqfp2,
          fastq3 = fastqfp3,
          fastq4 = fastqfp4,
          rg ="'@RG\\tID:" + RG_ID + "\\tSM:" + RG_SM + "\\tPL:" + RG_PL + "\\tPU:" + RG_PU + "\\tLB:" + RG_LB + "'",
          ref_fasta = ref_fasta,
          bwa_ref_fasta_index = ref_fasta_index,
          ref_dict = ref_dict,
          ref_bwt = ref_bwt,
          ref_sa = ref_sa,
          ref_amb = ref_amb,
          ref_ann = ref_ann,
          ref_pac = ref_pac,
          threads_bwa = threads_bwa,
          mem_bwa = mem_bwa,
          threads_samsort = threads_samsort,
          mem_samsort = mem_samsort,
  }
    #File aln_bam = "${bambwa}.bam"
    #File aln_bam_index = "${bambwa}.bam.bai"

  call MarkDuplicates{
    input:
         in_bam=AlignBwa.aln_bam,
         in_bam_index=AlignBwa.aln_bam_index,
         java_options=java_options,
         gatk_options=gatk_options,
         mem_dedup = mem_dedup,
         threads_dedup = threads_dedup,
  }
    #File out_bam = "${out_bam_file}"
    #File out_bam_index = "${out_bam_file_index}"
    #File dup_metrics = "${dup_metrics_file}"

  call baseRecalibrator{
    input:
         in_bam=MarkDuplicates.out_bam,
         in_bam_index=MarkDuplicates.out_bam_index,
         java_options=java_options,
         gatk_options=gatk_options,
         mem_bqsr = mem_bqsr,
         threads_bqsr = threads_bqsr,
         ref_fasta =  ref_fasta,
         ref_index =  ref_fasta_index,
         ref_dict =   ref_dict,
         ref_alt  =   ref_alt,
         bqsr_known_sites =   bqsr_known_sites,
         bqsr_known_sites_indexes =   bqsr_known_sites_indexes,
         intervals = intervals,
  }
    #File out_bqsr_table = "${out_bqsr_table_file}"
    #File out_bam = "${out_bam_file}"
    #File out_bam_index = "${out_bam_file_index}"

  call CollectHsMetrics{
    input:
         in_bam = baseRecalibrator.out_bam,
         in_bam_index = baseRecalibrator.out_bam_index,
         java_options=java_options,
         gatk_options=gatk_options,
         threads_hsmet = threads_hsmet,
         mem_hsmet = mem_hsmet,
         ref_fasta =  ref_fasta,
         ref_index =  ref_fasta_index,
         ref_dict =   ref_dict,
         target_intervals = intervals,
         probe_intervals = probe_intervals,
  }
    #File out_hs_metics = "${out_hs_file}"
    #File per_target_cov = "${out_pt_file}"

  call CallableLoci{
    input:
         in_bam = baseRecalibrator.out_bam,
         in_bam_index = baseRecalibrator.out_bam_index,
         mincalldepth = mincalldepth,
         threads_hsmet = threads_hsmet,
         mem_hsmet = mem_hsmet,
         ref_fasta =  ref_fasta,
         ref_index =  ref_fasta_index,
         ref_dict =   ref_dict,
         ref_alt = ref_alt,
	 target_intervals = intervals,
  }
    #File out_callable_bed = "${out_bed_file}"
    #File out_callable_summary = "${out_summary_file}"
    #File out_failed_bed = "${out_failed_file}"

  call HC_GVCF{
    input:
        in_bam = baseRecalibrator.out_bam,
        in_bam_index = baseRecalibrator.out_bam_index,
        sample = dataset,
        java_options=java_options,
        gatk_options=gatk_options,
        HaplotypeCaller_options=HaplotypeCaller_options,
        mem_hc = mem_hc,
        threads_hc = threads_hc,
        ref_fasta =  ref_fasta,
        ref_index =  ref_fasta_index,
        ref_dict =   ref_dict,
        ref_alt  =   ref_alt,
        intervals = intervals,
        dbSNP = dbSNP,
        dbSNP_index = dbSNP_index,
  }
    #File gvcf = "${out_gvcf_file}"
    #File gvcf_index = "${out_gvcf_file_index}"

  call genotypeGVCF {
    input:
      in_gvcf = HC_GVCF.gvcf,
      in_gvcf_index = HC_GVCF.gvcf_index,
      java_options=java_options,
      gatk_options=gatk_options,
      mem_genotype = mem_genotype,
      threads_genotype = threads_genotype,
      ref_fasta =  ref_fasta,
      ref_index =  ref_fasta_index,
      ref_dict =   ref_dict,
      ref_alt  =   ref_alt,
      intervals = intervals,
      dbSNP = dbSNP,
      dbSNP_index = dbSNP_index,
  }
   #File vcf = "${out_vcf_file}"
   #File vcf_index = "${out_vcf_file_index}"

}


task AlignBwa {
  String out
  File fastq1
  File fastq2
  File? fastq3
  File? fastq4
  File ref_fasta
  File bwa_ref_fasta_index
  File ref_dict
  File ref_bwt
  File ref_sa
  File ref_amb
  File ref_ann
  File ref_pac

  String? options=" -K 100000000 -Y -M "
  String rg
  Int threads_bwa
  String mem_bwa
  Int threads_samsort
  String mem_samsort

  String bambwa = out + ".bwa"

  String out1 = out + "-L1"
  String out2 = out + "-L2"
  String bambwa1 = out1 + ".bwa"
  String bambwa2 = out2 + ".bwa"

  command {
        bwa mem \
          ${options} \
          ${"-t " + threads_bwa} \
          ${"-R " + rg} \
          ${ref_fasta} \
          ${fastq1} \
          ${fastq2} > ${out1}.sam
  
        sambamba view -S -f bam ${"-t " + threads_samsort} ${out1}.sam > ${out1}.bam 
        sambamba sort ${"-t " + threads_samsort} -o ${bambwa1}.bam ${out1}.bam
        sambamba index ${"-t " + threads_samsort} ${bambwa1}.bam
    
        bwa mem \
          ${options} \
          ${"-t " + threads_bwa} \
          ${"-R " + rg} \
          ${ref_fasta} \
          ${fastq3} ${fastq4} > ${out2}.sam
        
        sambamba view -S -f bam ${"-t " + threads_samsort} ${out2}.sam > ${out2}.bam 
        sambamba sort ${"-t " + threads_samsort} -o ${bambwa2}.bam ${out2}.bam
        sambamba index ${"-t " + threads_samsort} ${bambwa2}.bam

        sambamba merge \
          ${"-t " + threads_samsort} \
          ${bambwa}.bam \
          ${bambwa1}.bam ${bambwa2}.bam

        sambamba index -t 4 ${bambwa}.bam
    }
    
  output {
        File aln_bam = "${bambwa}.bam"
        File aln_bam_index = "${bambwa}.bam.bai"
    }
  
  runtime {
        cpu : threads_bwa
        memory : mem_samsort
    }
}

task MarkDuplicates {
  File in_bam
  File in_bam_index
  String out_base = basename(in_bam,".bwa.bam")
  String out_bam_file = out_base + ".dedup.bam"
  String out_bam_file_index = out_base + ".dedup.bai"
  String dup_metrics_file = out_base + ".dupmetric"
  String? java_options
  String? gatk_options
  Int threads_dedup
  String mem_dedup

  command {
        /app/gatk4.py MarkDuplicates \
             ${"--java-options " + java_options} \
             --INPUT ${in_bam} \
             --OUTPUT ${out_bam_file} \
             --METRICS_FILE ${dup_metrics_file} \
             --CREATE_INDEX \
             ${gatk_options}
    }
  
  output {
        File out_bam = "${out_bam_file}"
        File out_bam_index = "${out_bam_file_index}"
        File dup_metrics = "${dup_metrics_file}"
    }
  
  runtime {
        cpu : threads_dedup
        memory : mem_dedup
    }
}

task baseRecalibrator {
  File in_bam
  File in_bam_index
  String out_base = basename(in_bam,".dedup.bam")
  String out_bqsr_table_file = out_base + ".dedup.recal.table"
  String out_bam_file = out_base + ".dedup.recal.bam"
  String out_bam_file_index = out_base + ".dedup.recal.bai"
  String? java_options
  String? gatk_options
  File ref_fasta
  File ref_index
  File ref_dict
  File ref_alt
  Array[File] bqsr_known_sites
  Array[File] bqsr_known_sites_indexes
  File? intervals

  # runtime
  Int threads_bqsr
  String mem_bqsr

  command {
        /app/gatk4.py BaseRecalibrator \
            ${"--java-options " + java_options} \
            -R ${ref_fasta} \
            -I ${in_bam} \
            --known-sites ${sep=' --known-sites ' bqsr_known_sites} \
            ${gatk_options} \
            -O ${out_bqsr_table_file}
        /app/gatk4.py ApplyBQSR \
            ${"--java-options " + java_options} \
            -I ${in_bam} \
            -O ${out_bam_file} \
            --emit-original-quals true \
            -bqsr ${out_bqsr_table_file} \
            --create-output-bam-index \
            ${gatk_options}
    }
  
  output {
        File out_bqsr_table = "${out_bqsr_table_file}"
        File out_bam = "${out_bam_file}"
        File out_bam_index = "${out_bam_file_index}"
    }
  
  runtime {
      cpu : threads_bqsr
      memory : mem_bqsr
    }
}

task CollectHsMetrics {
  File in_bam
  File in_bam_index
  String out_base = basename(in_bam,".bam")
  String out_hs_file = out_base + ".HsMetrics"
  String out_pt_file = out_base + ".PerTarget"
  File target_intervals
  File probe_intervals
  File ref_fasta
  File ref_index
  File ref_dict
  String? java_options
  String? gatk_options
  Int threads_hsmet
  String mem_hsmet

    command {
        gatk4.py CollectHsMetrics \
             ${"--java-options " + java_options} \
             -I ${in_bam} \
             -O ${out_hs_file} \
             -R ${ref_fasta} \
             -TARGET_INTERVALS ${target_intervals} \
             -BAIT_INTERVALS ${probe_intervals} \
             -PER_TARGET_COVERAGE ${out_pt_file} \
             ${gatk_options}
    }
    output {
        File out_hs_metrics = "${out_hs_file}"
        File per_target_cov = "${out_pt_file}"
    }
    runtime {
        cpu : threads_hsmet
        memory : mem_hsmet
    }
}

task CallableLoci {
  File in_bam
  File in_bam_index
  String out_base = basename(in_bam,".dedup.recal.bam")
  String out_bed_file = out_base + ".callable.bed"
  String out_summary_file = out_base + ".callable.summary"
  String out_failed_file = out_base + ".failed_regions.bed"
  File target_intervals
  File ref_fasta
  File ref_index
  File ref_dict
  File ref_alt
  Int mincalldepth
  String? java_options
  Int threads_hsmet
  String mem_hsmet

    command {
        gatk3.py -T CallableLoci \
             ${"--java-options " + java_options} \
	     -R ${ref_fasta} \
             -L ${target_intervals} \
             -I ${in_bam} \
             -o ${out_bed_file} \
             --minDepth ${mincalldepth} \
             --summary ${out_summary_file}

        grep -v CALLABLE ${out_bed_file} > ${out_failed_file}
    }
    output {
        File out_callable_bed = "${out_bed_file}"
        File out_callable_summary = "${out_summary_file}"
        File out_failed_bed = "${out_failed_file}"
    }
    runtime {
        cpu : threads_hsmet
        memory : mem_hsmet
    }
}

task HC_GVCF {
  File in_bam
  File in_bam_index
  String sample
  String in_bam_bn = basename(in_bam, '.dedup.recal.bam')
  String out_gvcf_file = sample + ".hc.gvcf.gz"
  String out_gvcf_file_index = out_gvcf_file + ".tbi"
  String? java_options
  String? gatk_options
  String? HaplotypeCaller_options
  File ref_fasta
  File ref_index
  File ref_dict
  File ref_alt
  File? dbSNP
  File? dbSNP_index
  File? intervals

  # runtime
  Int threads_hc
  String mem_hc

  command {
        gatk4.py HaplotypeCaller \
            ${"--java-options " + java_options} \
            -R ${ref_fasta} \
            ${"--dbsnp " + dbSNP} \
            ${"--native-pair-hmm-threads " + threads_hc} \
            ${"-L " + intervals} \
            -I ${in_bam} \
            -O ${out_gvcf_file} \
            -ERC GVCF \
            ${HaplotypeCaller_options} \
            ${gatk_options}
    }
  
  output {
        File gvcf = "${out_gvcf_file}"
        File gvcf_index = "${out_gvcf_file_index}"
    }
  
  runtime {
      cpu : threads_hc
      memory : mem_hc
    }
}

task genotypeGVCF {
  File in_gvcf
  File in_gvcf_index
  String gvcf_bn = basename(in_gvcf, '.gvcf.gz')
  String out_vcf_file = gvcf_bn + ".gt.vcf.gz"
  String out_vcf_file_index = out_vcf_file + ".tbi"
  String? java_options
  String? gatk_options
  File ref_fasta
  File ref_index
  File ref_dict
  File ref_alt
  File? dbSNP
  File? dbSNP_index
  File? intervals

  # runtime
  Int threads_genotype
  String mem_genotype

  command {
      gatk4.py GenotypeGVCFs \
            ${"--java-options " + java_options} \
            -R ${ref_fasta} \
            ${"--dbsnp " + dbSNP} \
            ${"-L " + intervals} \
            -V ${in_gvcf} \
            -O ${out_vcf_file} \
            ${gatk_options}
    }
  
  output {
        File vcf = "${out_vcf_file}"
        File vcf_index = "${out_vcf_file_index}"
    }
  
  runtime {
        cpu : threads_genotype
        memory : mem_genotype
    }
}


