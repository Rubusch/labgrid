def test_shell_command(shell):
    shell.run_check("ls -l")
    #stdout, stderr, returncode = shell.run('cat /proc/version')
    #assert returncode == 0
    #assert stdout
    #assert not stderr
    #assert 'Linux' in stdout[0]

    #stdout, stderr, returncode = shell.run('false')
    #assert returncode != 0
    #assert not stdout
    #assert not stderr
