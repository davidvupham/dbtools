# Performance and Optimization

## Profiling

Don't guess—measure!

```python
import cProfile
cProfile.run('my_function()')
```

## Optimization Tips

1. Use built-in functions (written in C).
2. Use local variables (faster access than global).
3. Use `slots` for classes with many instances.
4. Use Generators for large data.
