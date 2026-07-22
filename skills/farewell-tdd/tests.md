# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```python
# GOOD: Tests observable behavior
def test_user_can_checkout_with_valid_cart():
    cart = create_cart()
    cart.add(product)
    result = checkout(cart, payment_method)
    assert result.status == "confirmed"
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```python
# BAD: Tests implementation details
def test_checkout_calls_payment_service():
    mock_payment = Mock(spec=PaymentService)
    checkout(cart, mock_payment)
    mock_payment.process.assert_called_once_with(cart.total)
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT

```python
# BAD: Bypasses interface to verify
def test_create_user_saves_to_database():
    create_user(name="Alice")
    row = db.query("SELECT * FROM users WHERE name = ?", ["Alice"])
    assert row is not None

# GOOD: Verifies through interface
def test_create_user_makes_user_retrievable():
    user = create_user(name="Alice")
    retrieved = get_user(user.id)
    assert retrieved.name == "Alice"
```

**Tautological tests**: Expected value restates the implementation.

```python
# BAD: Expected value recomputed same way as code
def test_calculate_total_sums():
    items = [{"price": 10}, {"price": 5}]
    expected = sum(i["price"] for i in items)
    assert calculate_total(items) == expected

# GOOD: Expected value is independent, known literal
def test_calculate_total_sums():
    assert calculate_total([{"price": 10}, {"price": 5}]) == 15
```
