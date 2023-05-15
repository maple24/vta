## Listener
- remove test
in start_suite
test.tests.remove(test.tests[0])
- add tags to test
in start_test
test.tags.add("skip")
- pass testcase
in start_test
test.body.create_keyword(name='Log', args=['Keyword added by listener!'])

## Visitor
- Cannot access execution context