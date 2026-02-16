# Remove ignored_files.txt from mirror and push cleaned history
java -jar C:/Users/beren/bfg.jar --delete-files ignored_files.txt --no-blob-protection C:/Users/beren/repo-clean.git
Set-Location C:/Users/beren/repo-clean.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
$found = git rev-list --objects --all | Select-String 'ignored_files.txt' -SimpleMatch
if ($found) {
    Write-Output 'BLOB_STILL_PRESENT'
    $found
} else {
    Write-Output 'BLOB_REMOVED'
    git push --mirror origin --force
}
