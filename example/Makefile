SRC_FILE := source.txt ## source filename
TGT_FILE := target.txt ## target filename

$(TGT_FILE): $(SRC_FILE)
	cp $(SRC_FILE) $(TGT_FILE)

.PHONY: copy
copy: $(TGT_FILE) ## copy a file from SRC_FILE to TGT_FILE
