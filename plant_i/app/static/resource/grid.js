class Grid {
    constructor($target, gridOptions) {
        this.grid = null;
        this.$el = $target;
        this.gridOptions = gridOptions;
        this.init($target);
        this.defaultOptions = {};
        this.selectData = null;
    }

    init($target) {
        let _this = this;

        this.defaultOptions = {
            selectable: "multiple, row",
            sortable: true,
            pageable: false,
            resizable: true,
            //toolbar: ["excel","pdf"],
            excel: {
                allPages: true
            },
            reorderable: {
                rows: true
            },
        };

        // 병합 옵션 설정
        if (this.gridOptions.mergeCells) {
            // 셀 병합 시 ui가 애매해지기 때문에 모든 셀에 border 적용
            _this.applyBordersToAllCells();
            _this.makeMergeCellCondition();
        }

        // cell의 text-align 설정 - align: 'center' or 'right' or 'left'
        _this.setCellAlign();


        let options = { ...this.defaultOptions, ...this.gridOptions };
        this.$el = $target.kendoGrid(options);
        this.grid = this.$el.data("kendoGrid");
    }

    setCellAlign() {
        let columns = this.gridOptions.columns;
        columns.forEach(function (item) {
            if (item.align) {
                item.attributes = function (dataItem) {
                    return { style: `text-align: ${item.align}` };
                };
            }
        });
    }

    // border 적용
    applyBordersToAllCells() {
        let _this = this;
        let columns = _this.gridOptions.columns;

        columns.forEach(function (item) {
            item.attributes = function (dataItem) {
                let dataView = dataItem.parent();
                let currentIndex = dataView.indexOf(dataItem);
                let isLastRow = currentIndex === dataView.length - 1;

                if (isLastRow) {
                    return {
                        style: "border-left: 1px solid #ddd;"
                    };
                } else {
                    return {
                        style: "border-left: 1px solid #ddd; border-bottom: 1px solid #ddd"
                    };
                }
            };
        });
    }

    makeMergeCellCondition() {
        let _this = this;
        let mergeCells = _this.gridOptions.mergeCells;
        let columns = _this.gridOptions.columns;

        // 각 mergeCell마다 attrubute 설정
        mergeCells.forEach(function (colName, index) {
            columns.forEach(function (item) {
                if (colName === item.field) {
                    item.attributes = function (dataItem) {
                        return _this.getMergeCellAttributes(dataItem, index);
                    };
                    item.templates = _this.getMergeCellTemplates;
                }
            });
        });
    }

    getMergeCellAttributes(dataItem, colIndex) {
        let dataView = dataItem.parent();
        let currentIndex = dataView.indexOf(dataItem);
        let prevItem = currentIndex === 0 ? null : dataView.at(currentIndex - 1);
        let nextItem = dataView.at(++currentIndex);
        let rowSpan = 1;
        let mergeCells = this.gridOptions.mergeCells;

        // 두 번째 row부터 이전 row와 비교하여 같은 값이면 hidden 처리
        if (prevItem) {
            let canMerge = true;

            // 그룹화 종속 구현
            if (colIndex > 0) {
                if (dataItem[mergeCells[colIndex - 1]] !== prevItem[mergeCells[colIndex - 1]]) {
                    canMerge = false;
                }
            }
            if (canMerge && dataItem[mergeCells[colIndex]] === prevItem[mergeCells[colIndex]]) {
                return { hidden: 'hidden' };
            }
        }

        // 그룹화 시작 row에서 rowspan 모두 계산
        while (nextItem) {
            if (colIndex > 0) {
                if (dataItem[mergeCells[colIndex - 1]] !== nextItem[mergeCells[colIndex - 1]]) {
                    break;
                }
            }

            if (dataItem[mergeCells[colIndex]] === nextItem[mergeCells[colIndex]]) {
                rowSpan++;
            } else {
                break;
            }

            nextItem = dataView.at(++currentIndex);
        }

        // 스타일 설정
        let styleString = 'border-bottom: 1px solid #ddd';
        if (currentIndex === dataView.length) {
            styleString = '';  // 마지막 행을 포함한 그룹에서는 border-bottom 제거
        }

        return { rowSpan, style: styleString };
    }


    getMergeCellTemplates({ field_name })  {
        return `<strong>${kendo.htmlEncode(field_name)}</strong>`
    }

    setData(data) {
        this.grid.setDataSource(data);
    }

    getData() {
        return this.grid.dataSource.data();
    }

    getSelect() {
        let _this = this;
        let items = [];
        let rows = _this.grid.select();
        rows.each(function (e) {
            let dataItem = _this.grid.dataItem(this);
            dataItem.__index = $(this).index();
            items.push(dataItem);
        });
        
        return items
    }

    // 행이동 - 다중 이동(체크박스)
    changeOrder(direction) {
        let _this = this;
        let selectedItems = _this.getSelect();

        let first = selectedItems.some(function (item) {
            return item.__index === 0;
        });
        let last = selectedItems.some(function (item) {
            return item.__index === _this.grid.dataSource.data().length - 1;
        });

        if ((direction == 'U' && first) || (direction == 'D' && last)) {
            Alert.alert('', '선택된 행이 이동할 수 없습니다.');
            return;
        }

        selectedItems.sort(function (a, b) {
            return (direction == 'D') ? b.__index - a.__index : a.__index - b.__index;
        });
        $.each(selectedItems, function (index, item) {
            let currentIndex = item.__index;
            let targetIndex = (direction == 'D') ? currentIndex + 1 : currentIndex - 1;
            if (targetIndex >= 0 && targetIndex < _this.grid.dataSource.data().length) {
                _this.grid.dataSource.remove(item);
                _this.grid.dataSource.insert(targetIndex, item);
            }
        });

        // 선택행 유지
        _this.grid.clearSelection();
        $.each(selectedItems, function (index, item) {
            _this.grid.select(_this.grid.table.find("tr[data-uid='" + item.uid + "']"));
        })
        
    }

    setValue(key, data) { // 선택된 row에 대해서 setValue
        let selectedItem = this.grid.select()
        if (selectedItem.length > 0) {
            let dataItem = this.grid.dataItem(selectedItem);
            dataItem.set(key, data);
        }
    }

    addRow(location) {
        let _this = this
        let columns = _this.gridOptions.columns;
        let data = {};
        let datasource = _this.grid.dataSource;
        let count = 0

        columns.forEach(function (item) {
            data[item.field] = '';
        })
        if (location == 'end') {
            count = datasource.data().length + 1;
        }

        datasource.insert(count, data);

    }

    removeSelectedRow() {
        this.grid.removeRow(this.grid.select());
    }

    //setValue(rowIndex, key, data) { // index로 지정하여 setValue
    //    let dataItem = this.grid.dataSource.at(rowIndex);
    //    if (dataItem) {
    //        dataItem.set(key, data)
    //    }
    //}

}

class TreeGrid {
    constructor($target, gridOptions) {
        this.grid = null;
        this.$el = $target;
        this.gridOptions = gridOptions;
        this.init($target);
        this.defaultOptions = {};
        this.selectData = null;
    }

    init($target) {
        let _this = this;

        this.defaultOptions = {
            selectable: true,
            sortable: true,
            filterable: true,
            resizable: true,
            reorderable: true,
            pageable: false,
            editable: {
                mode: "inline",
            },
            scrollable: true,
            navigatable: true,
        };

        let options = { ...this.defaultOptions, ...this.gridOptions };
        this.$el = $target.kendoTreeList(options);
        this.grid = this.$el.data("kendoTreeList");
    }

    setTreeDataSource(data, f_options) {
        let dataSource = new kendo.data.TreeListDataSource({
            data: data,
            schema: {
                model: {
                    id: f_options.id,
                    parentId: f_options.parentId,
                    fields: f_options.fields,
                },
                parse: function(data) {
                    // 데이터가 로드될 때 확장 상태를 설정
                    data.forEach(function(item) {
                        item.expanded = false;  // 모든 항목을 확장 상태로 설정
                    });
                    return data;
                }
            }
        });
        this.grid.setDataSource(dataSource);
    }

    setTreeDataOnly(data) {
        this.grid.dataSource.data(data);
    }

    expandAll() {
        let grid = this.grid;
        
        // TreeList의 최상위 항목만 확장
        grid.expand(grid.tbody.find(">tr")); 
    }
    
    collapseAll() {
        let grid = this.grid;
    
        // TreeList의 최상위 항목만 축소
        grid.collapse(grid.tbody.find(">tr")); 
    }
    
    // 단일 데이터
    getTreeData() {
        let _this = this;
        let item = _this.grid.dataItem(_this.grid.select());
        return item;
    }

    // 전체
    getData() {
        return this.grid.dataSource.data();
    }

    // 다중, 단일 선택 모두 가능
    getSelect() {
        let _this = this;
        let items = [];
        let rows = _this.grid.select();
        rows.each(function (e) {
            let dataItem = _this.grid.dataItem(this);
            items.push(dataItem);
        });
        
        return items
    }

    // 순서 변경 up
    moveUp() {                  // 미사용
        let _this = this;
        let rows = _this.grid.select();
        if (rows.length > 0) {
            conosle.log('aa')
            let datItem = _this.grid.dataItem(rows);
            let index = _this.grid.indexOf(datItem);
            if (index > 0) {
                let prevItem = _this.grid.dataSource.at(index - 1);
                _this.grid.dataSource.remove(datItem);
                _this.grid.dataSource.insert(index - 1, datItem);
                _this.grid.dataSource.remove(prevItem);
                _this.grid.dataSource.insert(index, prevItem);
                _this.grid.select(rows);
            }
        }
    }

    moveRow(direction) {        // 미사용
        let _this = this;
        let selectedRow = _this.grid.select();
        let selectedDataItem = _this.grid.dataItem(selectedRow);

        if (!selectedDataItem) {
            alert("Please select a row to move.");
            return;
        }

        let parentDataItem = _this.grid.dataSource.get(selectedDataItem.parentId);
        //let siblings = parentDataItem ? parentDataItem.children.data() : _this.grid.dataSource.data();
        let siblings = parentDataItem ? _this.grid.dataSource.childNodes(parentDataItem) : _this.grid.dataSource.data();
        console.log(siblings)
        let index = siblings.indexOf(selectedDataItem);
        console.log(index)
        if (direction === "up" && index > 0) {
            siblings.splice(index, 1);
            siblings.splice(index - 1, 0, selectedDataItem);
        } else if (direction === "down" && index < siblings.length - 1) {
            siblings.splice(index, 1);
            siblings.splice(index + 1, 0, selectedDataItem);
        }

        //_this.grid.dataSource.read();
        // insert remove
    }
}