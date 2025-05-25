// Fetch user statistics when page loads
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/total_users')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const statsContainer = document.getElementById('userStats');
                        statsContainer.innerHTML = `
                            <div class="stat-card">
                                <h3>Total Users</h3>
                                <p>${data.total_users}</p>
                            </div>
                            <div class="stat-card">
                                <h3>Buyers</h3>
                                <p>${data.roles.buyers}</p>
                            </div>
                            <div class="stat-card">
                                <h3>Sellers</h3>
                                <p>${data.roles.sellers}</p>
                            </div>
                            <div class="stat-card">
                                <h3>Riders</h3>
                                <p>${data.roles.riders}</p>
                            </div>
                            <div class="stat-card">
                                <h3>Admins</h3>
                                <p>${data.roles.admins}</p>
                            </div>
                        `;
                    } else {
                        document.getElementById('userStats').innerHTML = 
                            '<p class="error">Error loading user statistics</p>';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('userStats').innerHTML = 
                        '<p class="error">Error loading user statistics</p>';
                });

            // Fetch and display order statistics
            fetchOrderStats();
        });

        let combinedChart = null;
        let allMonthlyData = [];
        let allYearlyData = [];
        let currentChartType = 'monthly';

        function fetchOrderStats() {
            fetch('/order_stats')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        allMonthlyData = data.monthly;
                        allYearlyData = data.yearly;
                        
                        // Populate year select dropdown
                        populateYearSelect();
                        
                        // Render initial chart
                        renderChart(allMonthlyData, allYearlyData);
                        
                        // Update summary
                        updateChartSummary(allMonthlyData, 'monthly');
                    } else {
                        console.error('Error loading order stats:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        function populateYearSelect() {
            const yearSelect = document.getElementById('yearSelect');
            
            // Get unique years from monthly data
            const years = [...new Set(allMonthlyData.map(item => item.year))].sort((a, b) => b - a);
            
            // Clear existing options except "All Years"
            while (yearSelect.options.length > 1) {
                yearSelect.remove(1);
            }
            
            // Add year options
            years.forEach(year => {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                yearSelect.appendChild(option);
            });
        }

        function renderChart(monthlyData, yearlyData) {
            const ctx = document.getElementById('combinedChart').getContext('2d');
            
            // Prepare monthly chart data
            const monthlyLabels = monthlyData.map(item => `${item.month_name} ${item.year}`);
            const monthlySales = monthlyData.map(item => item.total_sales);
            const monthlyOrders = monthlyData.map(item => item.order_count);

            // Prepare yearly chart data
            const yearlyLabels = yearlyData.map(item => item.year);
            const yearlySales = yearlyData.map(item => item.total_sales);
            const yearlyOrders = yearlyData.map(item => item.order_count);

            // Destroy previous chart if it exists
            if (combinedChart) {
                combinedChart.destroy();
            }

            // Create combined chart
            combinedChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: monthlyLabels,
                    datasets: [
                        {
                            label: 'Total Sales (₱)',
                            data: monthlySales,
                            backgroundColor: 'rgba(106, 13, 173, 0.7)',
                            borderColor: 'rgba(106, 13, 173, 1)',
                            borderWidth: 1,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Number of Orders',
                            data: monthlyOrders,
                            backgroundColor: 'rgba(156, 77, 255, 0.7)',
                            borderColor: 'rgba(156, 77, 255, 1)',
                            borderWidth: 1,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Monthly Sales & Orders',
                            font: {
                                size: 16
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.datasetIndex === 0) {
                                        label += '₱' + context.parsed.y.toLocaleString();
                                    } else {
                                        label += context.parsed.y.toLocaleString();
                                    }
                                    return label;
                                }
                            }
                        },
                        zoom: {
                            zoom: {
                                wheel: {
                                    enabled: true,
                                },
                                pinch: {
                                    enabled: true
                                },
                                mode: 'x',
                            },
                            pan: {
                                enabled: true,
                                mode: 'x',
                            },
                            limits: {
                                x: { min: 'original', max: 'original' },
                                y: { min: 'original', max: 'original' }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Sales (₱)'
                            },
                            grid: {
                                drawOnChartArea: false
                            },
                            ticks: {
                                callback: function(value) {
                                    return '₱' + value.toLocaleString();
                                }
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Orders'
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });

            // Store data for tab switching
            window.chartData = {
                monthly: {
                    labels: monthlyLabels,
                    sales: monthlySales,
                    orders: monthlyOrders,
                    title: 'Monthly Sales & Orders',
                    fullData: monthlyData
                },
                yearly: {
                    labels: yearlyLabels,
                    sales: yearlySales,
                    orders: yearlyOrders,
                    title: 'Yearly Sales & Orders',
                    fullData: yearlyData
                }
            };
        }

        function showChart(type) {
            if (!combinedChart || !window.chartData) return;

            currentChartType = type;
            
            // Update active tab
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            event.currentTarget.classList.add('active');

            // Show/hide controls
            document.getElementById('monthlyControls').style.display = 
                type === 'monthly' ? 'flex' : 'none';
            document.getElementById('yearlyControls').style.display = 
                type === 'yearly' ? 'flex' : 'none';

            // Update chart data
            const data = window.chartData[type];
            combinedChart.data.labels = data.labels;
            combinedChart.data.datasets[0].data = data.sales;
            combinedChart.data.datasets[1].data = data.orders;
            combinedChart.options.plugins.title.text = data.title;
            combinedChart.update();
            
            // Update summary
            updateChartSummary(data.fullData, type);
        }

        function filterByYear() {
            const yearSelect = document.getElementById('yearSelect');
            const selectedYear = yearSelect.value;
            
            if (selectedYear === 'all') {
                // Show all data
                window.chartData.monthly.labels = allMonthlyData.map(item => `${item.month_name} ${item.year}`);
                window.chartData.monthly.sales = allMonthlyData.map(item => item.total_sales);
                window.chartData.monthly.orders = allMonthlyData.map(item => item.order_count);
                window.chartData.monthly.fullData = allMonthlyData;
            } else {
                // Filter data by selected year
                const filteredData = allMonthlyData.filter(item => item.year == selectedYear);
                window.chartData.monthly.labels = filteredData.map(item => `${item.month_name} ${item.year}`);
                window.chartData.monthly.sales = filteredData.map(item => item.total_sales);
                window.chartData.monthly.orders = filteredData.map(item => item.order_count);
                window.chartData.monthly.fullData = filteredData;
            }
            
            if (currentChartType === 'monthly') {
                combinedChart.data.labels = window.chartData.monthly.labels;
                combinedChart.data.datasets[0].data = window.chartData.monthly.sales;
                combinedChart.data.datasets[1].data = window.chartData.monthly.orders;
                combinedChart.update();
                
                // Update summary
                updateChartSummary(window.chartData.monthly.fullData, 'monthly');
            }
        }

        function filterByYearRange() {
            const startYear = parseInt(document.getElementById('startYear').value);
            const endYear = parseInt(document.getElementById('endYear').value);
            
            if (isNaN(startYear)) {
                alert('Please enter a valid start year');
                return;
            }
            
            if (isNaN(endYear)) {
                alert('Please enter a valid end year');
                return;
            }
            
            if (startYear > endYear) {
                alert('Start year cannot be after end year');
                return;
            }
            
            // Filter data by year range
            const filteredData = allYearlyData.filter(item => 
                item.year >= startYear && item.year <= endYear
            );
            
            window.chartData.yearly.labels = filteredData.map(item => item.year);
            window.chartData.yearly.sales = filteredData.map(item => item.total_sales);
            window.chartData.yearly.orders = filteredData.map(item => item.order_count);
            window.chartData.yearly.fullData = filteredData;
            
            if (currentChartType === 'yearly') {
                combinedChart.data.labels = window.chartData.yearly.labels;
                combinedChart.data.datasets[0].data = window.chartData.yearly.sales;
                combinedChart.data.datasets[1].data = window.chartData.yearly.orders;
                combinedChart.update();
                
                // Update summary
                updateChartSummary(window.chartData.yearly.fullData, 'yearly');
            }
        }

        function resetZoom() {
            if (combinedChart) {
                combinedChart.resetZoom();
            }
        }

        function updateChartSummary(data, type) {
            const summaryContainer = document.getElementById('chartSummaryContent');
            
            if (data.length === 0) {
                summaryContainer.innerHTML = '<p>No data available for the selected period</p>';
                return;
            }
            
            // Calculate totals
            const totalSales = data.reduce((sum, item) => sum + item.total_sales, 0);
            const totalOrders = data.reduce((sum, item) => sum + item.order_count, 0);
            const avgOrderValue = totalSales / totalOrders;
            
            // Find best and worst periods
            let bestPeriod = data[0];
            let worstPeriod = data[0];
            
            data.forEach(item => {
                if (item.total_sales > bestPeriod.total_sales) bestPeriod = item;
                if (item.total_sales < worstPeriod.total_sales) worstPeriod = item;
            });
            
            // Format summary
            summaryContainer.innerHTML = `
                <div class="summary-card">
                    <h3>Total Sales</h3>
                    <p>₱${totalSales.toLocaleString()}</p>
                </div>
                <div class="summary-card">
                    <h3>Total Orders</h3>
                    <p>${totalOrders.toLocaleString()}</p>
                </div>
                <div class="summary-card">
                    <h3>Avg. Order Value</h3>
                    <p>₱${avgOrderValue.toFixed(2).toLocaleString()}</p>
                </div>
                <div class="summary-card highlight">
                    <h3>Best ${type === 'monthly' ? 'Month' : 'Year'}</h3>
                    <p>${type === 'monthly' ? bestPeriod.month_name + ' ' + bestPeriod.year : bestPeriod.year}</p>
                    <p class="value">₱${bestPeriod.total_sales.toLocaleString()}</p>
                </div>
                <div class="summary-card lowlight">
                    <h3>Worst ${type === 'monthly' ? 'Month' : 'Year'}</h3>
                    <p>${type === 'monthly' ? worstPeriod.month_name + ' ' + worstPeriod.year : worstPeriod.year}</p>
                    <p class="value">₱${worstPeriod.total_sales.toLocaleString()}</p>
                </div>
            `;
        }