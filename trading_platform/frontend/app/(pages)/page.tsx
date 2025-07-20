'use client';

import Header from "@/components/layout/Header";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import ClientExecutionTable from "@/components/dashboard/ClientExecutionTable";
import TokenSelector from "@/components/dashboard/TokenSelector";
import TradeConfigPanel from "@/components/dashboard/TradeConfigPanel";
import { useDashboardStore } from "@/lib/store/useDashboardStore";

export default function OrderDashboard() {
  const { executeAllOrders, tradeConfig } = useDashboardStore();

  return (
    <div className="flex flex-col gap-8">
      <Header title="Order Management" />

      {/* Top Configuration Panel */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 items-end">
            <TokenSelector />
            <TradeConfigPanel />
          </div>
        </CardContent>
      </Card>

      {/* Bottom Client Table Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Clients</CardTitle>
        </CardHeader>
        <CardContent>
          <ClientExecutionTable />
        </CardContent>
        <CardFooter>
          <Button size="lg" className="ml-auto" onClick={executeAllOrders}>
            Execute All ({tradeConfig.buyOrSell})
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
