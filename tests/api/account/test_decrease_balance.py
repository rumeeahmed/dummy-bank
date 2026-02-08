import uuid
from typing import Any, Callable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from structlog.stdlib import BoundLogger

from dummy_bank.domain import Account, Customer
from dummy_bank.repository import AccountsRepository, CustomerRepository


class TestAccountNotFound:
    @pytest.mark.asyncio
    async def test(
        self,
        test_client: TestClient,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        logger: BoundLogger,
    ) -> None:
        payload = {"amount": 102.99}
        response = test_client.post(
            f"/dummy-bank/v1/accounts/{uuid.uuid4()}/withdraw", json=payload
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "account not found"}


class TestDecreaseBalance:
    @pytest.mark.asyncio
    async def test(
        self,
        test_client: TestClient,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        logger: BoundLogger,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        payload = {"amount": 7.87}
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=100.50, customer_id=customer.id)
        await account_repository.save_account(account)

        loaded_customer = await customer_repository.load_customer_with_id(customer.id)
        assert loaded_customer is not None

        response = test_client.post(
            f"/dummy-bank/v1/accounts/{account.id}/withdraw", json=payload
        )
        assert response.status_code == 200
        assert response.json()["account_balance"] == 9263

    @pytest.mark.asyncio
    async def test_withdraw_more_than_balance(
        self,
        test_client: TestClient,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        logger: BoundLogger,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        payload = {"amount": 200}
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=100.50, customer_id=customer.id)
        await account_repository.save_account(account)

        loaded_customer = await customer_repository.load_customer_with_id(customer.id)
        assert loaded_customer is not None

        response = test_client.post(
            f"/dummy-bank/v1/accounts/{account.id}/withdraw", json=payload
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "insufficient funds for this transaction"

    @pytest.mark.parametrize(
        argnames=["field", "value"],
        argvalues=[
            ("balance", None),
            ("balance", "remove"),
            ("balance", -12),
        ],
    )
    @pytest.mark.asyncio
    async def test_bad_payload(
        self, test_client: TestClient, field: str, value: Any
    ) -> None:
        payload: dict = {}

        if value is not None and value == "remove":
            payload.pop(field, None)
        else:
            payload[field] = value

        response = test_client.post(
            f"/dummy-bank/v1/accounts/{uuid.uuid4()}/withdraw", json=payload
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_multiple_requests(
        self,
        app: FastAPI,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        payload = {"amount": 100}
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=1000, customer_id=customer.id)
        await account_repository.save_account(account)

        loaded_customer = await customer_repository.load_customer_with_id(customer.id)
        assert loaded_customer is not None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            for i in range(10):
                await client.post(
                    f"/dummy-bank/v1/accounts/{account.id}/withdraw", json=payload
                )

            response = await client.get(
                "/dummy-bank/v1/accounts", params={"customer_id": str(customer.id)}
            )
            assert response.status_code == 200
            assert response.json()["results"][0]["account_balance"] == 0
