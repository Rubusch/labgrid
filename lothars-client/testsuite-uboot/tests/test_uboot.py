def test_uboot_command(uboot):
    uboot.run_check("printenv")
    #stdout, stderr, returncode = shell.run('cat /proc/version')
    #assert returncode == 0
    #assert stdout
    #assert not stderr
    #assert 'Linux' in stdout[0]

    #stdout, stderr, returncode = shell.run('false')
    #assert returncode != 0
    #assert not stdout
    #assert not stderr
