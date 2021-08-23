all : module.tmp 
	@echo Complete

module.tmp: TestData_base.xlsx read_file.py
	@python read_file.py
	@touch module.tmp
#	@touch TestData_make.xlsx

clean:
	@rm -f *tmp
	@rm -f *csv
	@echo "Cleaned up"
