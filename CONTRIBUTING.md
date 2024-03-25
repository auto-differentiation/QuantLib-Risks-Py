# How to contribute

We love pull requests from everyone. By participating in this project, you agree to abide
by our [code of conduct](CODE_OF_CONDUCT.md).

Note that this fork is importing all changes from the QuantLib-SWIG repository on each
release. Changes related to QuantLib's own Python bindings will be included in each new
release. 
Contributions to this repository should only be made if they are related to building
the Python bindings for quantlib-risks (enabled with XAD).

1.  Fork, then clone the repository:

```bash
git clone https://github.com/yourusername/quantlib-risks.git
```

2.  Follow the [Build Instructions](README.md) to setup the dependencies and 
    build the software. Make sure all tests pass.

3.  Create a feature branch, typically based on master, for your change

```bash
git checkout -b feature/my-change main
```

4.  Make your changes, adding tests as you go, and commit. Again, make sure all 
    tests pass.

5.  Push your fork 

6.  [Submit a pull request][pr]. Not that you will have to sign the [Contributor License Agreement][cla] 
    before the PR can be merged.

At this point, you are depending on the core team to review your request. 
We may suggest changes, improvements, or alternatives. 
We strive to at least comment on a pull request within 3 business days. 
After feedback has been given, we expect a response within 2 weeks, 
after which we may close the pull request if it isn't showing activity.

Some things that will highly increase the chance that your pull request gets
accepted:

-   Discuss the change you wish to make via issue or email

-   Write good tests for all added features

-   Write good commit messages (short one-liner, followed by a blank line, 
    followed by a more detailed explanation)


[pr]: https://github.com/auto-differentiation/quantlib-risks/compare/

[cla]: https://gist.github.com/auto-differentiation-dev/5c6121c3f341e2de710fa034e9ff3263
