library(HIBAG)

args <- commandArgs(TRUE)
ethnicity=args[1]
print(ethnicity)
if(ethnicity == 'European') trained.Rdata = "/app/models/European-HLA4-hg19.RData"
if(ethnicity == 'Asian') trained.Rdata = "/app/models/Asian-HLA4-hg19.RData"
if(ethnicity == 'Hispanic') trained.Rdata = "/app/models/Hispanic-HLA4-hg19.RData"
if(ethnicity == 'African') trained.Rdata = "/app/models/African-HLA4-hg19.RData"

# Load the published parameter estimates from European ancestry
load(trained.Rdata)
A.model <- hlaModelFromObj(HLA4[['A']])
B.model <- hlaModelFromObj(HLA4[['B']])
C.model <- hlaModelFromObj(HLA4[['C']])
rm('HLA4')

# Import your PLINK BED file
yourgeno <- hlaBED2Geno(bed.fn="plink.bed", fam.fn="plink.fam", bim.fn="plink.bim")
summary(yourgeno)

# HLA imputation at HLA-A

A.guess <- predict(A.model, yourgeno, type="response+prob",match.type='Position')


B.guess <- predict(B.model, yourgeno, type="response+prob",match.type='Position')


C.guess <- predict(C.model, yourgeno, type="response+prob",match.type='Position')


write.csv(
	data.frame(A_allele1=A.guess$value$allele1, A_allele2=A.guess$value$allele2, A_prob=A.guess$value$prob,
			B_allele1=B.guess$value$allele1, B_allele2=B.guess$value$allele2, B_prob=B.guess$value$prob,
		    C_allele1=C.guess$value$allele1, C_allele2=C.guess$value$allele2, C_prob=C.guess$value$prob),
		    	file='HIBAG_output.csv', row.names=FALSE)
