import uuid
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from structlog.stdlib import BoundLogger

from dummy_bank.api.lock_manager import LockManager
from dummy_bank.repository import AccountsRepository, CustomerRepository

from ...make_domain_objects import MakeAccount, MakeCustomer


class TestAccountNotFound:
    @pytest.mark.asyncio
    async def test_account_1_not_found(
        self,
        test_client: AsyncClient,
        customer_repository: CustomerRepository,
        make_customer: MakeCustomer,
        account_repository: AccountsRepository,
        make_account: MakeAccount,
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account_2 = make_account(customer_id=customer.id)
        await account_repository.save_account(account_2)

        payload = {"account_id": str(account_2.id), "amount": 100}

        response = await test_client.post(
            f"/dummy-bank/v1/accounts/{uuid.uuid4()}/transfer", json=payload
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "account not found"}

    @pytest.mark.asyncio
    async def test_account_2_not_found(
        self,
        test_client: AsyncClient,
        customer_repository: CustomerRepository,
        make_customer: MakeCustomer,
        account_repository: AccountsRepository,
        make_account: MakeAccount,
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account_1 = make_account(customer_id=customer.id)
        await account_repository.save_account(account_1)

        payload = {"account_id": str(uuid.uuid4()), "amount": 100}

        response = await test_client.post(
            f"/dummy-bank/v1/accounts/{account_1.id}/transfer", json=payload
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "account not found"}

    @pytest.mark.asyncio
    async def test_customer_both_customers_not_found(
        self, test_client: AsyncClient
    ) -> None:
        payload = {"amount": 102.99, "account_id": str(uuid.uuid4())}

        response = await test_client.post(
            f"/dummy-bank/v1/accounts/{uuid.uuid4()}/transfer", json=payload
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "account not found"}


class TestTransferBalance:
    @pytest.mark.asyncio
    async def test(
        self,
        test_client: AsyncClient,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: MakeCustomer,
        make_account: MakeAccount,
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=100.50, customer_id=customer.id)
        await account_repository.save_account(account)

        account_2 = make_account(customer_id=customer.id, account_balance=94.27)
        await account_repository.save_account(account_2)

        payload = {"amount": 7.87, "account_id": str(account_2.id)}

        response = await test_client.post(
            f"/dummy-bank/v1/accounts/{account.id}/transfer", json=payload
        )
        assert response.status_code == 200
        assert response.json()[0]["account_balance"] == 9263
        assert response.json()[1]["account_balance"] == 10214

    @pytest.mark.asyncio
    async def test_transfer_more_than_balance(
        self,
        test_client: AsyncClient,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: MakeCustomer,
        make_account: MakeAccount,
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=100.50, customer_id=customer.id)
        await account_repository.save_account(account)

        account_2 = make_account(customer_id=customer.id, account_balance=94.27)
        await account_repository.save_account(account_2)

        payload = {"amount": 1000, "account_id": str(account_2.id)}

        response = await test_client.post(
            f"/dummy-bank/v1/accounts/{account.id}/transfer", json=payload
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
        self,
        test_client: AsyncClient,
        customer_repository: CustomerRepository,
        field: str,
        value: Any,
    ) -> None:
        payload: dict = {}

        if value is not None and value == "remove":
            payload.pop(field, None)
        else:
            payload[field] = value

        response = await test_client.post(
            f"/dummy-bank/v1/accounts/{uuid.uuid4()}/transfer", json=payload
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_multiple_requests(
        self,
        app: FastAPI,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: MakeCustomer,
        make_account: MakeAccount,
        logger: BoundLogger,
        lock_manager: LockManager,
        test_client: AsyncClient,
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=1000, customer_id=customer.id)
        await account_repository.save_account(account)

        account_2 = make_account(customer_id=customer.id, account_balance=0)
        await account_repository.save_account(account_2)

        payload = {"amount": 100, "account_id": str(account_2.id)}

        for i in range(10):
            response = await test_client.post(
                f"/dummy-bank/v1/accounts/{account.id}/transfer", json=payload
            )
            assert response.status_code == 200

        response = await test_client.get(
            "/dummy-bank/v1/accounts", params={"customer_id": str(customer.id)}
        )
        response_json = response.json()

        assert response_json["results"][0]["account_balance"] == 0
        assert response_json["results"][1]["account_balance"] == 100000
