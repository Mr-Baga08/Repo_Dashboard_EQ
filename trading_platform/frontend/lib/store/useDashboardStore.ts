import { create } from 'zustand';

// --- Types and Interfaces ---
interface Client {
  id: string;
  name: string;
  client_id: string;
}

interface TradeConfig {
  tokenSymbol: string;
  tokenExchange: string;
  tradeType: 'MTF' | 'INTRADAY';
  orderType: 'MARKET' | 'LTP';
  buyOrSell: 'BUY' | 'SELL';
}

interface Quantities {
  [clientId: string]: number;
}

// Interface for the real-time P/L data
interface RealtimePL {
  [clientId: string]: number;
}

interface DashboardState {
  clients: Client[];
  quantities: Quantities;
  tradeConfig: TradeConfig;
  realtimePL: RealtimePL; // Added for real-time P/L
  fetchClients: () => Promise<void>;
  setQuantity: (clientId: string, quantity: number) => void;
  setTradeConfig: (config: Partial<TradeConfig>) => void;
  executeAllOrders: () => Promise<void>;
  updatePL: (clientId: string, pnl: number) => void; // Added action for P/L updates
}

// --- Store Definition ---
export const useDashboardStore = create<DashboardState>((set, get) => ({
  // --- State Properties ---
  clients: [],
  quantities: {},
  tradeConfig: {
    tokenSymbol: 'RELIANCE', // Default value
    tokenExchange: 'NSE',      // Default value
    tradeType: 'INTRADAY',
    orderType: 'MARKET',
    buyOrSell: 'BUY',
  },
  realtimePL: {}, // Initial state for real-time P/L

  // --- State Actions ---
  fetchClients: async () => {
    try {
      // Note: The API path should not include `/v1` if using FastAPI's default router setup.
      // Adjust if your backend router has a prefix.
      const response = await fetch('/api/clients');
      if (!response.ok) throw new Error('Failed to fetch clients');
      const clients = await response.json();
      set({ clients });
    } catch (error) {
      console.error("Error fetching clients:", error);
      // In a real app, you'd set an error state here
    }
  },

  setQuantity: (clientId, quantity) => {
    set((state) => ({
      quantities: {
        ...state.quantities,
        [clientId]: quantity,
      },
    }));
  },

  setTradeConfig: (config) => {
    set((state) => ({
      tradeConfig: {
        ...state.tradeConfig,
        ...config,
      },
    }));
  },

  updatePL: (clientId, pnl) => {
    set((state) => ({
      realtimePL: {
        ...state.realtimePL,
        [clientId]: pnl,
      },
    }));
  },

  executeAllOrders: async () => {
    const { tradeConfig, quantities } = get();

    const client_orders = Object.entries(quantities)
      .filter(([, quantity]) => quantity > 0)
      .map(([clientId, quantity]) => ({
        client_id: clientId,
        quantity,
      }));

    if (client_orders.length === 0) {
      // Using console.warn instead of alert for better development experience
      console.warn("No orders to execute. Please set quantities for clients.");
      return;
    }

    const payload = {
      token_symbol: tradeConfig.tokenSymbol,
      token_exchange: tradeConfig.tokenExchange,
      trade_type: tradeConfig.tradeType,
      order_type: tradeConfig.orderType,
      buy_or_sell: tradeConfig.buyOrSell,
      client_orders,
    };

    try {
      const response = await fetch('/api/orders/execute-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to execute orders');
      }

      const result = await response.json();
      console.log('Execution Result:', result);
      // Reset quantities after successful execution
      set({ quantities: {} });

    } catch (error) {
      console.error("Error executing orders:", error);
      // Handle alerts or notifications in the UI component instead of the store
    }
  },
}));
