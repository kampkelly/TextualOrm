# Set of commands
install:
	@echo "Installing packages..."
	pip-compile requirements.in && pip-sync requirements.txt
