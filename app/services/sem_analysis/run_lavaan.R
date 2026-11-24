# ==============================================================================
# run_lavaan.R - Companion R Script for Component 2 (CFA & SEM)
# Psychometric Learning Analytics Framework (Project ID: J26-DS-310)
# ==============================================================================
# Usage:
#   Rscript app/services/sem_analysis/run_lavaan.R [optional_data_path]
#
# Requirements in R:
#   install.packages(c("lavaan", "semTools"))
# ==============================================================================

args <- commandArgs(trailingOnly = TRUE)
data_path <- ifelse(length(args) > 0, args[1], "data/processed/component2_survey_clean.csv")

cat("----------------------------------------------------------------------\n")
cat("Component 2: Algorithmic Trust & Verification Analysis (R / lavaan)\n")
cat("Loading cleaned dataset from:", data_path, "\n")
cat("----------------------------------------------------------------------\n")

if (!file.exists(data_path)) {
  stop(paste("Data file not found at:", data_path))
}

data <- read.csv(data_path, header = TRUE, stringsAsFactors = FALSE)
cat("Dataset dimensions: ", nrow(data), " rows, ", ncol(data), " columns.\n\n")

# Check if lavaan is installed
if (!requireNamespace("lavaan", quietly = TRUE)) {
  cat("NOTE: 'lavaan' package is not currently installed in this R environment.\n")
  cat("To install, run in R: install.packages('lavaan')\n")
  cat("The Python semopy service serves as the verified execution engine in the framework.\n")
  quit(status = 0)
}

library(lavaan)

# 1. CFA Measurement Model Specification
cfa_model <- '
  AT =~ AT1 + AT2 + AT3 + AT4 + AT5 + AT6
  VB =~ VB1 + VB2 + VB3 + VB4 + VB5
  PU =~ PU1 + PU2 + PU3 + PU4 + PU5
  AD =~ AD1 + AD2 + AD3 + AD4 + AD5
  LC =~ LC1 + LC2 + LC3 + LC4 + LC5
'

cat("=== 1. ESTIMATING CONFIRMATORY FACTOR ANALYSIS (CFA) ===\n")
cfa_fit <- cfa(cfa_model, data = data, estimator = "MLR", missing = "listwise")
summary(cfa_fit, fit.measures = TRUE, standardized = TRUE)

# 2. SEM Structural Equation Model Specification
sem_model <- '
  # Measurement Model
  AT =~ AT1 + AT2 + AT3 + AT4 + AT5 + AT6
  VB =~ VB1 + VB2 + VB3 + VB4 + VB5
  PU =~ PU1 + PU2 + PU3 + PU4 + PU5
  AD =~ AD1 + AD2 + AD3 + AD4 + AD5
  LC =~ LC1 + LC2 + LC3 + LC4 + LC5

  # Structural Regressions
  VB ~ a1*AT + a2*PU
  AD ~ c1_p*AT + c2_p*PU + b1*VB
  LC ~ d1_p*AT + d2_p*PU + b2*VB

  # Indirect Effects (Mediation via VB)
  ind_AT_AD := a1 * b1
  ind_AT_LC := a1 * b2
  ind_PU_AD := a2 * b1
  ind_PU_LC := a2 * b2

  # Total Effects
  tot_AT_AD := c1_p + (a1 * b1)
  tot_PU_AD := c2_p + (a2 * b1)
  tot_AT_LC := d1_p + (a1 * b2)
  tot_PU_LC := d2_p + (a2 * b2)
'

cat("\n=== 2. ESTIMATING STRUCTURAL EQUATION MODEL (SEM) ===\n")
sem_fit <- sem(sem_model, data = data, estimator = "MLR", missing = "listwise")
summary(sem_fit, fit.measures = TRUE, standardized = TRUE, rsquare = TRUE)

cat("\nAnalysis completed successfully.\n")
