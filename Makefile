# In your main Makefile
ifeq ($(OS),Windows_NT)
    include tools/Windows.mak
else
    include tools/Linux.mak
endif
