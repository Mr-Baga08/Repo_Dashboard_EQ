import create from 'zustand';

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

interface DashboardState {
  clients: Client[];
  quantities: Quantities;
  tradeConfig: TradeConfig;
  fetchClients: () => Promise<void>;
  setQuantity: (clientId: string, quantity: number) => void;
  setTradeConfig: (config: Partial<TradeConfig>) => void;
  executeAllOrders: () => Promise<void>;
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

  // --- State Actions ---
  fetchClients: async () => {
    try {
      const response = await fetch('/api/v1/clients');
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

  executeAllOrders: async () => {
    const { tradeConfig, quantities } = get();

    const client_orders = Object.entries(quantities)
      .filter(([, quantity]) => quantity > 0)
      .map(([clientId, quantity]) => ({
        client_id: clientId,
        quantity,
      }));

    if (client_orders.length === 0) {
      alert("No orders to execute. Please set quantities for clients.");
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
      const response = await fetch('/api/v1/orders/execute-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to execute orders');
      }

      const result = await response.json();
      alert('Orders executed successfully!');
      console.log('Execution Result:', result);
      // Reset quantities after successful execution
      set({ quantities: {} });

    } catch (error) {
      console.error("Error executing orders:", error);
      alert(`Execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },
}));
