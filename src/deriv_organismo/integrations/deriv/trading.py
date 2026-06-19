"""Real Deriv trading gateway — sends proposal/buy via WebSocket.

Replaces the stub gateway with real Deriv API calls through the
persistent DerivClient connection.
"""

from __future__ import annotations

from deriv_organismo.domain.accounts import AccountContext


class DerivTradingGateway:
    """Gateway for real Deriv trading operations via WebSocket.

    Uses the same authorized WebSocket connection as the rest of the app.
    If no client is provided, falls back to stub behavior for backward compat.
    """

    def __init__(self, client=None) -> None:
        self.client = client
        self._stub_mode = client is None
        self._last_proposal: dict | None = None
        self._last_buy: dict | None = None

    def build_proposal_request(
        self,
        *,
        account: AccountContext,
        symbol: str,
        amount: float,
        contract_type: str = "CALL",
        duration: int = 5,
        duration_unit: str = "m",
        currency: str = "USD",
        basis: str = "stake",
    ) -> dict:
        """Build a proposal request payload."""
        return {
            "symbol": symbol,
            "amount": amount,
            "basis": basis,
            "contract_type": contract_type,
            "currency": currency,
            "duration": duration,
            "duration_unit": duration_unit,
            "passthrough": {
                "account_id": account.account_id,
                "tenant_id": account.tenant_id,
                "account_slug": account.account_slug,
                "mode": account.mode,
            },
        }

    def build_buy_request(self, *, proposal_id: str, amount: float) -> dict:
        """Build a buy request payload."""
        return {"proposal_id": proposal_id, "price": amount}

    async def request_proposal(self, payload: dict) -> dict:
        """Request a real proposal from Deriv via WebSocket.

        Args:
            payload: Dict with symbol, amount, contract_type, etc.

        Returns:
            A dict with 'proposal' key containing the proposal response.
        """
        if self._stub_mode:
            # Stub fallback for backward compatibility
            proposal_id = payload.get("passthrough", {}).get("account_id", "acc") + "_proposal"
            result = {"proposal": {"id": proposal_id, "request": payload}}
            self._last_proposal = result
            return result

        symbol = payload.get("symbol", payload.get("proposal", "R_100"))
        amount = payload.get("amount", 10)
        contract_type = payload.get("contract_type", "CALL")
        duration = payload.get("duration", 5)
        duration_unit = payload.get("duration_unit", "m")
        currency = payload.get("currency", "USD")
        basis = payload.get("basis", "stake")

        response = await self.client.request_proposal(
            symbol=str(symbol),
            amount=float(amount),
            contract_type=str(contract_type),
            duration=int(duration),
            duration_unit=str(duration_unit),
            currency=str(currency),
            basis=str(basis),
        )
        self._last_proposal = response
        return response

    async def submit_buy(self, payload: dict) -> dict:
        """Execute a real buy on Deriv via WebSocket.

        Args:
            payload: Dict with 'buy' (proposal_id) and 'price'.

        Returns:
            A dict with 'buy' key containing the contract response.
        """
        if self._stub_mode:
            # Stub fallback for backward compatibility
            proposal_id = payload.get("buy", payload.get("proposal_id", "contract"))
            result = {
                "buy": {
                    "contract_id": str(proposal_id) + "_contract",
                    "status": "open",
                    "request": payload,
                }
            }
            self._last_buy = result
            return result

        proposal_id = payload.get("buy", payload.get("proposal_id", ""))
        price = float(payload.get("price", payload.get("amount", 10)))

        response = await self.client.buy_contract(str(proposal_id), price)
        self._last_buy = response
        return response

    async def check_contract(self, contract_id: int) -> dict:
        """Check the outcome of a contract."""
        if self._stub_mode:
            return {"proposal_open_contract": {"contract_id": contract_id, "status": "open", "profit": 0}}
        return await self.client.check_contract(contract_id)

    @property
    def last_proposal_id(self) -> str | None:
        if self._last_proposal:
            prop = self._last_proposal.get("proposal", {})
            return prop.get("id")
        return None

    @property
    def last_contract_id(self) -> int | None:
        if self._last_buy:
            buy = self._last_buy.get("buy", {})
            cid = buy.get("contract_id")
            return int(cid) if cid else None
        return None

    @property
    def last_contract_status(self) -> str | None:
        if self._last_buy:
            buy = self._last_buy.get("buy", {})
            return buy.get("status")
        return None
