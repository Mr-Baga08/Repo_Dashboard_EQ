'use client';

import { useDashboardStore } from '@/lib/store/useDashboardStore';
import { Button } from '@/components/ui/Button';

export default function TradeConfigPanel() {
  const { tradeConfig, setTradeConfig } = useDashboardStore();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end col-span-1 md:col-span-3">
      {/* Trade Type */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Trade Type</label>
        <div className="flex gap-2">
          <Button
            onClick={() => setTradeConfig({ tradeType: 'MTF' })}
            variant={tradeConfig.tradeType === 'MTF' ? 'default' : 'outline'}
            className="w-full"
          >
            MTF
          </Button>
          <Button
            onClick={() => setTradeConfig({ tradeType: 'INTRADAY' })}
            variant={tradeConfig.tradeType === 'INTRADAY' ? 'default' : 'outline'}
            className="w-full"
          >
            Intraday / Delivery
          </Button>
        </div>
      </div>

      {/* Order Type */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Order Type</label>
        <div className="flex gap-2">
          <Button
            onClick={() => setTradeConfig({ orderType: 'MARKET' })}
            variant={tradeConfig.orderType === 'MARKET' ? 'default' : 'outline'}
            className="w-full"
          >
            Market
          </Button>
          <Button
            onClick={() => setTradeConfig({ orderType: 'LTP' })}
            variant={tradeConfig.orderType === 'LTP' ? 'default' : 'outline'}
            className="w-full"
          >
            LTP
          </Button>
        </div>
      </div>

      {/* Execution Actions */}
      <div className="flex gap-2 justify-self-end self-end">
        <Button
          onClick={() => setTradeConfig({ buyOrSell: 'BUY' })}
          className={tradeConfig.buyOrSell === 'BUY' ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-600/50 hover:bg-blue-700/80 text-white'}
        >
          BUY
        </Button>
        <Button
          onClick={() => setTradeConfig({ buyOrSell: 'SELL' })}
          className={tradeConfig.buyOrSell === 'SELL' ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-red-600/50 hover:bg-red-700/80 text-white'}
        >
          SELL
        </Button>
        <Button variant="secondary">EXIT</Button>
      </div>
    </div>
  );
}