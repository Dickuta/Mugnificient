#!/bin/bash
# Move duplicate/old files to _trash folder

cd /Users/admin/workspaces/_active-projects/mugnificient

# Move duplicate root scripts (now in scripts/)
mv build.sh _trash/ 2>/dev/null
mv clean.sh _trash/ 2>/dev/null
mv start.sh _trash/ 2>/dev/null
mv stop.sh _trash/ 2>/dev/null
mv setup.sh _trash/ 2>/dev/null
mv run.sh _trash/ 2>/dev/null
mv test.sh _trash/ 2>/dev/null

# Move old test scripts
mv run_docker_test.sh _trash/ 2>/dev/null
mv run_tests.sh _trash/ 2>/dev/null
mv test_docker.sh _trash/ 2>/dev/null

# Move database file
mv eshop.db _trash/ 2>/dev/null

# Remove cache directories
rm -rf .pytest_cache
rm -rf backend/.pytest_cache

echo "✅ Files moved to _trash/"
echo ""
echo "Remaining in root:"
ls -la
