import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 12,
    total: 0,
    total_pages: 0
  });
  
  // Filter states
  const [search, setSearch] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // Selected product for detail view
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showDetail, setShowDetail] = useState(false);

  // Fetch products and categories on load
  useEffect(() => {
    fetchCategories();
    fetchProducts();
  }, []);

  // Fetch products when filters change
  useEffect(() => {
    fetchProducts();
  }, [pagination.page, sortBy, sortOrder]);

  const fetchCategories = async () => {
    try {
      const response = await apiClient.get('/categories');
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        limit: pagination.limit,
      };
      
      if (search) params.search = search;
      if (categoryId) params.category_id = categoryId;
      if (minPrice) params.min_price = minPrice;
      if (maxPrice) params.max_price = maxPrice;
      if (sortBy) params.sort_by = sortBy;
      if (sortOrder) params.sort_order = sortOrder;
      
      const response = await apiClient.get('/products', { params });
      setProducts(response.data.data || []);
      setPagination(response.data.pagination || { page: 1, limit: 12, total: 0, total_pages: 0 });
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPagination(prev => ({ ...prev, page: 1 }));
    fetchProducts();
  };

  const handleFilterChange = () => {
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const handleProductClick = (product) => {
    setSelectedProduct(product);
    setShowDetail(true);
  };

  const getCategoryName = (categoryId) => {
    const cat = categories.find(c => c.id === categoryId);
    return cat ? cat.name : 'Unknown';
  };

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Products</h1>
        <p className="text-gray-600 mt-1">Browse our product catalog with real-time search and filters</p>
      </div>

      {/* Search and Filters */}
      <div className="card mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
          {/* Search */}
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="flex gap-2">
              <input
                type="text"
                className="input flex-1"
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                className="btn btn-primary btn-sm whitespace-nowrap"
                onClick={handleSearch}
              >
                Search
              </button>
            </div>
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              className="input"
              value={categoryId}
              onChange={(e) => {
                setCategoryId(e.target.value);
                handleFilterChange();
              }}
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>

          {/* Min Price */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min Price</label>
            <input
              type="number"
              className="input"
              placeholder="0"
              value={minPrice}
              onChange={(e) => {
                setMinPrice(e.target.value);
                handleFilterChange();
              }}
            />
          </div>

          {/* Max Price */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Price</label>
            <input
              type="number"
              className="input"
              placeholder="1000"
              value={maxPrice}
              onChange={(e) => {
                setMaxPrice(e.target.value);
                handleFilterChange();
              }}
            />
          </div>

          {/* Sort */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select
              className="input"
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                handleFilterChange();
              }}
            >
              <option value="">Default</option>
              <option value="price">Price</option>
              <option value="stock">Stock</option>
              <option value="created_at">Newest</option>
            </select>
          </div>
        </div>

        {/* Active Filters */}
        {(search || categoryId || minPrice || maxPrice || sortBy) && (
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-200">
            <span className="text-sm text-gray-600">Active filters:</span>
            {search && (
              <span className="badge badge-blue">
                Search: {search}
                <button
                  className="ml-1 hover:text-red-600"
                  onClick={() => { setSearch(''); handleSearch(); }}
                >
                  ×
                </button>
              </span>
            )}
            {categoryId && (
              <span className="badge badge-blue">
                Category: {getCategoryName(parseInt(categoryId))}
                <button
                  className="ml-1 hover:text-red-600"
                  onClick={() => { setCategoryId(''); handleFilterChange(); }}
                >
                  ×
                </button>
              </span>
            )}
            {minPrice && (
              <span className="badge badge-blue">
                Min: ${minPrice}
                <button
                  className="ml-1 hover:text-red-600"
                  onClick={() => { setMinPrice(''); handleFilterChange(); }}
                >
                  ×
                </button>
              </span>
            )}
            {maxPrice && (
              <span className="badge badge-blue">
                Max: ${maxPrice}
                <button
                  className="ml-1 hover:text-red-600"
                  onClick={() => { setMaxPrice(''); handleFilterChange(); }}
                >
                  ×
                </button>
              </span>
            )}
            {sortBy && (
              <span className="badge badge-blue">
                Sort: {sortBy} ({sortOrder})
                <button
                  className="ml-1 hover:text-red-600"
                  onClick={() => { setSortBy(''); handleFilterChange(); }}
                >
                  ×
                </button>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-600">
          Showing {products.length} of {pagination.total} products
        </p>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Show:</label>
          <select
            className="input py-1 px-2 w-20"
            value={pagination.limit}
            onChange={(e) => {
              setPagination(prev => ({ ...prev, limit: parseInt(e.target.value), page: 1 }));
            }}
          >
            <option value="12">12</option>
            <option value="24">24</option>
            <option value="48">48</option>
          </select>
        </div>
      </div>

      {/* Product Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading products...</div>
        </div>
      ) : products.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No products found matching your criteria</p>
          <button
            className="btn btn-primary mt-4"
            onClick={() => {
              setSearch('');
              setCategoryId('');
              setMinPrice('');
              setMaxPrice('');
              setSortBy('');
              fetchProducts();
            }}
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <div
              key={product.id}
              className="card hover:shadow-lg transition-shadow cursor-pointer flex flex-col"
              onClick={() => handleProductClick(product)}
            >
              {/* Product Image */}
              <div className="w-full h-48 bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/300x200?text=No+Image';
                    }}
                  />
                ) : (
                  <span className="text-gray-400 text-sm">No Image</span>
                )}
              </div>
              
              {/* Product Info */}
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 text-sm line-clamp-2">
                  {product.name}
                </h3>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                  {product.description || 'No description'}
                </p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-lg font-bold text-primary-600">
                    ${product.price.toFixed(2)}
                  </span>
                  <span className={`text-sm ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                  </span>
                </div>
                <div className="mt-2">
                  <span className="badge badge-gray text-xs">
                    {getCategoryName(product.category_id)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
          >
            Previous
          </button>
          
          <div className="flex gap-1">
            {Array.from({ length: Math.min(pagination.total_pages, 5) }, (_, i) => {
              let pageNum;
              if (pagination.total_pages <= 5) {
                pageNum = i + 1;
              } else if (pagination.page <= 3) {
                pageNum = i + 1;
              } else if (pagination.page >= pagination.total_pages - 2) {
                pageNum = pagination.total_pages - 4 + i;
              } else {
                pageNum = pagination.page - 2 + i;
              }
              return (
                <button
                  key={pageNum}
                  className={`px-3 py-1 rounded-lg text-sm font-medium ${
                    pageNum === pagination.page
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  onClick={() => handlePageChange(pageNum)}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page === pagination.total_pages}
          >
            Next
          </button>
        </div>
      )}

      {/* Product Detail Modal */}
      {showDetail && selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">{selectedProduct.name}</h2>
                <button
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                  onClick={() => setShowDetail(false)}
                >
                  ×
                </button>
              </div>
              
              <div className="w-full h-64 bg-gray-100 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
                {selectedProduct.image_url ? (
                  <img
                    src={selectedProduct.image_url}
                    alt={selectedProduct.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/600x400?text=No+Image';
                    }}
                  />
                ) : (
                  <span className="text-gray-400">No Image</span>
                )}
              </div>
              
              <div className="space-y-3">
                <p className="text-gray-700">{selectedProduct.description || 'No description available'}</p>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Price</p>
                    <p className="text-lg font-bold text-primary-600">${selectedProduct.price.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Stock</p>
                    <p className={`text-lg font-semibold ${selectedProduct.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedProduct.stock > 0 ? `${selectedProduct.stock} available` : 'Out of stock'}
                    </p>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Category</p>
                  <p className="font-medium">{getCategoryName(selectedProduct.category_id)}</p>
                </div>
                
                <div className="pt-4 border-t border-gray-200">
                  <button
                    className="btn btn-primary w-full"
                    onClick={() => setShowDetail(false)}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}