export const CardSkeleton = () => (
  <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm animate-pulse space-y-3">
    <div className="h-4 w-1/3 bg-gray-200 rounded-md"></div>
    <div className="h-8 w-2/3 bg-gray-200 rounded-lg"></div>
    <div className="h-3 w-1/2 bg-gray-150 rounded-md"></div>
  </div>
);

export const TableSkeleton = ({ rows = 5 }) => (
  <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-4 animate-pulse">
    <div className="h-6 w-1/4 bg-gray-200 rounded-md mb-4"></div>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex items-center justify-between space-x-4 py-2">
        <div className="h-4 w-1/4 bg-gray-200 rounded"></div>
        <div className="h-4 w-1/6 bg-gray-200 rounded"></div>
        <div className="h-4 w-1/5 bg-gray-200 rounded"></div>
        <div className="h-4 w-1/6 bg-gray-200 rounded"></div>
      </div>
    ))}
  </div>
);

export const ChartSkeleton = () => (
  <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm animate-pulse space-y-4">
    <div className="h-5 w-1/3 bg-gray-200 rounded-md"></div>
    <div className="h-56 w-full bg-gray-100 rounded-xl flex items-end p-4 space-x-3">
      <div className="w-1/6 h-2/3 bg-gray-200 rounded-t-md"></div>
      <div className="w-1/6 h-full bg-gray-200 rounded-t-md"></div>
      <div className="w-1/6 h-1/2 bg-gray-200 rounded-t-md"></div>
      <div className="w-1/6 h-4/5 bg-gray-200 rounded-t-md"></div>
      <div className="w-1/6 h-1/3 bg-gray-200 rounded-t-md"></div>
      <div className="w-1/6 h-3/4 bg-gray-200 rounded-t-md"></div>
    </div>
  </div>
);

export default CardSkeleton;
